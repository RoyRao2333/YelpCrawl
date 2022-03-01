import os
import csv
import time
import re
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# init driver
service = Service("/usr/local/bin/msedgedriver")
service.start()
driver = webdriver.Remote(service.service_url)

def find_element_by_xpath(self, xpath):
    return self.find_element(by=By.XPATH, value=xpath)


def makedir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)

def save_img(url, name):
    image_folder = os.getcwd() + "/results/img/"
    makedir(image_folder)
    image_path = os.path.join(image_folder, name + ".jpg")
    urlretrieve(url, image_path)

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
    parse(self, file)

    if find_element_by_xpath(self, "//*[@title='Next']").get_attribute("href") is None:
        return
    else:
        time.sleep(5)
        find_element_by_xpath(self, "//*[@title='Next']").click()
        crawl(self, file)

    file.flush()

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
    title = soup\
        .find("div", id="wrap")\
        .find("div", class_="arrange_unit arrange_unit--fill")\
        .find("h1")\
        .get_text()
    index = soup\
        .find("div", id="wrap")\
        .find("ul", class_="media-footer_inner")\
        .find("li", class_="media-footer_count")\
        .find("span", class_="media-count_current")\
        .get_text()
    img = soup\
        .find("div", id="wrap")\
        .find("img", class_="photo-box-img")\
        .attrs["src"]
    comment = soup\
        .find("div", id="wrap")\
        .find("div", class_="caption selected-photo-caption-text")\
        .get_text()
    date = soup \
        .find("div", id="wrap")\
        .find("div", class_="selected-photo-details")\
        .find("span")\
        .get_text()
    passport = soup \
        .find("div", id="wrap")\
        .find("div", class_="media-info")
    username = ""
    is_merchant = ""

    info = passport.find("ul", class_="user-passport-info")
    if info:
        username = info\
            .find("li", class_="user-name")\
            .find("a", id="dropdown_user-name")\
            .get_text()
        is_merchant = "No"
    else:
        username = passport\
            .find("li")\
            .find("strong")\
            .find("a")\
            .find("span")\
            .get_text()
        is_merchant = "Yes"

    image_name = title + " " + index
    save_img(img, image_name)
    writer.writerow([
        image_name,
        comment,
        username,
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
    csv_writer.writerow(["img", "comment", "username", "isMerchant", "date"])

    # do your job
    for store_url in get_input():
        driver.get(store_url)
        url = get_entrance(driver)
        driver.get(url)
        crawl(driver, output_file)

    # deinit
    output_file.close()
    driver.quit()