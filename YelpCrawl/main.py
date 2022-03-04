import os
import csv
import time
import re
import uuid
from urllib.request import urlretrieve
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from pathlib import Path

# init driver
option = webdriver.ChromeOptions()
# option.headless = True
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


def wait_for_staleness(self, element):
    WebDriverWait(self, 10).until(EC.staleness_of(element))


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


def crawl(self, file):
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
            next_element = wait_for_element_by_xpath(self, "//*[@id='lightbox-inner']/div[2]/div/div/div[2]/a[2]")

        except WebDriverException:
            try:
                close_element = wait_for_element_by_xpath(self, "//*[@id='lightbox-inner']/div[1]")
                close_element.click()
            except WebDriverException:
                pass

            return True

        else:
            if next_element.get_attribute("href") is None:
                try:
                    close_element = wait_for_element_by_xpath(self, "//*[@id='lightbox-inner']/div[1]")
                    close_element.click()
                except WebDriverException:
                    pass

                return True

            next_element.click()
            time.sleep(2)


def parse(self, file):
    writer = csv.writer(file)

    try:
        user_id = find_element_by_xpath(
            self,
            "//a[contains(@class, 'user-display-name')]"
        ).text
        is_merchant = "No"
    except WebDriverException:
        try:
            user_id = find_element_by_xpath(
                self,
                "//a[@data-analytics-label='biz-name']/span"
            ).text
            is_merchant = "Yes"
        except WebDriverException:
            user_id = ""
            is_merchant = ""

    try:
        tab_label = find_element_by_xpath(
            self,
            "//a[@role='tab'][contains(@class, 'is-selected')]/span[contains(@class, 'tab-link_label')]"
        ).text
    except WebDriverException:
        tab_label = ""

    try:
        comment = find_element_by_xpath(
            self,
            "//div[contains(@class, 'selected-photo-caption-text')]"
        ).text
    except WebDriverException:
        comment = ""

    try:
        index = find_element_by_xpath(
            self,
            "//span[@class='media-count_current']"
        ).text
    except WebDriverException:
        index = ""

    try:
        img = wait_for_element_by_xpath(
            self,
            "//img[@class='photo-box-img'][@loading='auto']"
        ).get_attribute("src")
    except WebDriverException:
        img = ""

    try:
        date = find_element_by_xpath(
            self,
            "//span[contains(@class, 'selected-photo-upload-date')]"
        ).text
    except WebDriverException:
        date = ""

    if img:
        image_name = f"[{tab_label}] {index}" if index else f"[{tab_label}] {uuid.uuid4().hex}"
        image_path = os.path.join(img_folder_path, image_name + ".jpg")
        save_img(img, image_path)
    else:
        image_name = "N/A"

    writer.writerow([
        tab_label,
        image_name,
        comment,
        user_id,
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
        crawl(driver, output_file)
        output_file.close()

        flag_writer = csv.writer(input_file)
        flag_writer.writerow()
        print("Business_id {} completed.".format(business_id))

    # deinit
    driver.quit()
