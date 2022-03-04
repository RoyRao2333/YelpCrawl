import os
import csv
import time
import re
import requests
from urllib.request import urlretrieve
from urllib.parse import urlparse, parse_qsl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
from pathlib import Path

# init driver
option = webdriver.ChromeOptions()
option.headless = True
driver = webdriver.Chrome(options=option)


def find_element_by_xpath(self, xpath):
    return self.find_element(by=By.XPATH, value=xpath)


def find_elements_by_xpath(self, xpath):
    return self.find_elements(by=By.XPATH, value=xpath)


def find_element_by_id(self, value):
    return self.find_elements(by=By.ID, value=value)


def wait_for_element_by_id(self, value):
    return WebDriverWait(self, 10).until(EC.presence_of_element_located((By.ID, value)))


def wait_for_element_by_xpath(self, value):
    return WebDriverWait(self, 10).until(EC.presence_of_element_located((By.XPATH, value)))


def find_elements_by_class_name(self, class_name):
    return self.find_elements(by=By.CLASS_NAME, value=class_name)


def makedir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)


def save_img(img_url, path):
    urlretrieve(img_url, path)


def get_input():
    csv_reader = csv.reader(input_file)
    input_list = list()

    for line in csv_reader:
        item = line[0]
        if item is not None and isinstance(item, str):
            input_list.append(item)

    return input_list


def crawl(self, file, retry: int):
    for tab_element in find_elements_by_xpath(self, "//*[@class='tab-link js-tab-link tab-link--nav js-tab-link--nav']"):
        tab_label = tab_element.get_attribute("data-media-tab-label")
        if tab_label in finished_tabs or tab_label == "all":
            continue

        tab_element.click()
        time.sleep(2)
        # click first image item
        find_element_by_xpath(self, "//*[@class='biz-shim js-lightbox-media-link js-analytics-click']").click()

        if iterate(self, file):
            finished_tabs.append(tab_label)
            print(f"Tab {tab_label} completed.")

        else:
            print("Process ended due to a network error. Retrying...")
            self.get(entrance_url)
            time.sleep(2)


def iterate(self, file) -> bool:
    while True:
        try:
            wait_for_element_by_id(self, "lightbox")
        except WebDriverException:
            return False
        else:
            parse(self, file)

        try:
            next_element = find_element_by_xpath(self, "//*[@id='lightbox-inner']/div[2]/div/div/div[2]/a[2]")
            close_element = find_element_by_xpath(self, "//*[@id='lightbox-inner']/div")

        except WebDriverException:
            return True

        else:
            if next_element.get_attribute("href") is None:
                close_element.click()
                return True

            time.sleep(1)
            next_element.click()


def parse(self, file):
    writer = csv.writer(file)
    outer_raw = self.page_source
    soup = BeautifulSoup(outer_raw, "lxml")
    tab_label = soup \
        .find("div", id="wrap") \
        .find("a", class_=re.compile(r".*tab-link.*is-selected.*")) \
        .find("span", class_="tab-link_label") \
        .get_text()

    inner_raw = requests.get(self.current_url).text
    soup = BeautifulSoup(inner_raw, "lxml")
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
        userid = ""
        is_merchant = "Yes"

    image_name = f"[{tab_label}] {index}"
    image_path = os.path.join(img_folder_path, image_name + ".jpg")
    save_img(img, image_path)
    writer.writerow([
        tab_label,
        image_name,
        comment,
        userid,
        is_merchant,
        date
    ])
    file.flush()
    print("Fetched " + image_name)


if __name__ == '__main__':
    makedir("./Desktop/YelpResults")

    input_path = Path(__file__).with_name("stores.csv")
    input_file = input_path.open(mode="r", encoding="utf-8-sig")

    # do your job
    for business_id in get_input():
        entrance_url = "https://www.yelp.com/biz_photos/" + business_id
        driver.get(entrance_url)

        finished_tabs = list()

        # prepare dirs
        folder_path = os.path.join("./Desktop/YelpResults/", business_id)
        makedir(folder_path)
        img_folder_path = os.path.join(folder_path, "img")
        makedir(img_folder_path)
        output_file_path = os.path.join(folder_path, "manifest.csv")

        output_file = open(output_file_path, "w", encoding="utf-8-sig")
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(["category", "img", "comment", "user_id", "is_merchant", "date"])
        crawl(driver, output_file, retry=0)
        output_file.close()

        # flag_writer = csv.writer(input_file)
        # flag_writer.writerow()
        print("Business_id {} completed.".format(business_id))

    # deinit
    driver.quit()
