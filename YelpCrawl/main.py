import os
import csv
import time
import re
from urllib.request import urlretrieve
from urllib.parse import urlparse, parse_qsl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# init driver
service = Service(os.path.join(os.getcwd(), "resource/msedgedriver"))
service.start()
driver = webdriver.Remote(service.service_url)


def find_element_by_xpath(self, xpath):
    return self.find_element(by=By.XPATH, value=xpath)


def makedir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)


def save_img(img_url, name):
    image_folder = os.getcwd() + "/results/img/"
    makedir(image_folder)
    image_path = os.path.join(image_folder, name + ".jpg")
    urlretrieve(img_url, image_path)


def get_input():
    input_file = open(os.getcwd() + "/stores.csv", mode="r", encoding="utf-8-sig")
    csv_reader = csv.reader(input_file)
    input_list = list()

    for line in csv_reader:
        item = line[0]
        if item is not None and isinstance(item, str):
            input_list.append(item)

    return input_list


def crawl(self, file):
    if find_element_by_xpath(self, "//*[@title='Next']") is None:
        print("Process ended due to a network error. Retrying...")
        self.refresh()
        time.sleep(2)
        crawl(self, file)
    else:
        parse(self, file)

    if find_element_by_xpath(self, "//*[@title='Next']").get_attribute("href") is None:
        print("Process completed.")
        return
    else:
        time.sleep(2)
        find_element_by_xpath(self, "//*[@title='Next']").click()
        crawl(self, file)


def get_entrance(self):
    raw = self.page_source
    soup = BeautifulSoup(raw, "lxml")
    div = soup.find("div", class_="media-landing_gallery photos")
    ul = div.find("ul")
    inner_url = "https://www.yelp.com" + ul.find("li").find("a").attrs["href"]
    return inner_url


def parse(self, file):
    writer = csv.writer(file)
    raw = self.page_source
    soup = BeautifulSoup(raw, "lxml")
    title = soup \
        .find("div", id="wrap") \
        .find("div", class_="arrange_unit arrange_unit--fill") \
        .find("h1") \
        .get_text()
    index = soup \
        .find("div", id="wrap") \
        .find("ul", class_="media-footer_inner") \
        .find("li", class_="media-footer_count") \
        .find("span", class_="media-count_current") \
        .get_text()
    img = soup \
        .find("div", id="wrap") \
        .find("img", class_="photo-box-img") \
        .attrs["src"]
    comment = soup \
        .find("div", id="wrap") \
        .find("div", class_="caption selected-photo-caption-text") \
        .get_text()
    date = soup \
        .find("div", id="wrap") \
        .find("div", class_="selected-photo-details") \
        .find("span") \
        .get_text()
    passport = soup \
        .find("div", id="wrap") \
        .find("div", class_="media-info")

    info = passport.find("ul", class_="user-passport-info")
    if info:
        userurl = "https://www.yelp.com/" + info \
            .find("li", class_="user-name") \
            .find("a", id="dropdown_user-name") \
            .attrs["href"]
        parsed = urlparse(userurl)
        params = dict(parse_qsl(parsed.query))
        userid = params["userid"]
        is_merchant = "No"
    else:
        merchant_url = soup \
            .find("link", attrs={"href": re.compile(r".*ios-app.*")}) \
            .attrs["href"]
        parsed = urlparse(merchant_url)
        params = dict(parse_qsl(parsed.query))
        userid = params["biz_id"]
        is_merchant = "Yes"

    image_name = title + " " + index
    save_img(img, image_name)
    writer.writerow([
        image_name,
        comment,
        userid,
        is_merchant,
        date
    ])
    file.flush()
    print("Fetched " + image_name)


if __name__ == '__main__':
    # get paths
    makedir(os.path.join(os.getcwd(), "results"))
    output_file = open(os.path.join(os.getcwd(), "results/manifest.csv"), "w", encoding="utf-8-sig")

    csv_writer = csv.writer(output_file)
    csv_writer.writerow(["img", "comment", "user_id", "is_merchant", "date"])

    # do your job
    for store_url in get_input():
        driver.get(store_url)
        url = get_entrance(driver)
        driver.get(url)
        crawl(driver, output_file)

    # deinit
    output_file.close()
    driver.quit()
