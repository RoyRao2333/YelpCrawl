import os
import csv
import time
import re
import pickle
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, urlencode, parse_qsl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from pathlib import Path

# init driver
option = webdriver.ChromeOptions()
# option.headless = True
driver = webdriver.Chrome(options=option)


def find_element_by_xpath(self, xpath):
    try:
        return self.find_element(by=By.XPATH, value=xpath)

    except WebDriverException:
        return None


def find_elements_by_xpath(self, xpath):
    try:
        return self.find_elements(by=By.XPATH, value=xpath)

    except WebDriverException:
        return list()


def find_element_by_id(self, value):
    try:
        return self.find_elements(by=By.ID, value=value)

    except WebDriverException:
        return None


def wait_for_element_by_id(self, value):
    try:
        return WebDriverWait(self, 10).until(ec.presence_of_element_located((By.ID, value)))

    except WebDriverException:
        return None


def wait_for_element_by_xpath(self, value):
    try:
        return WebDriverWait(self, 10).until(ec.presence_of_element_located((By.XPATH, value)))

    except WebDriverException:
        return None


def find_elements_by_class_name(self, class_name):
    try:
        return self.find_elements(by=By.CLASS_NAME, value=class_name)

    except WebDriverException:
        return list()


def makedir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)


def save_img(img_url, path) -> bool:
    try:
        response = urlopen(img_url)

    except (URLError, HTTPError):
        print("Image fetch failed.")
        return False

    try:
        with open(path, 'wb') as img_file:
            img_file.write(response.read())
        return True

    except OSError:
        print("Image save failed.")
        return False


def get_param_from_url(url: str, key: str):
    try:
        parsed = urlparse(url)
        params = dict(parse_qsl(parsed.query))
        return params[key] if params[key] is not None else ""

    except ValueError:
        return None


def get_input(file):
    csv_reader = csv.reader(file)
    input_list = list()

    for line in csv_reader:
        item = line[0]
        if item is not None and isinstance(item, str):
            input_list.append(item)

    return input_list


def crawl(self, output) -> bool:
    tab_list = find_elements_by_xpath(self, "//a[contains(@class, 'tab-link--nav')][contains(@class, 'js-tab-link--nav')]")
    if not tab_list:
        return False

    for tab_element in tab_list:
        try:
            tab_element.click()
        except WebDriverException:
            return False

        time.sleep(2)
        tab_label_e = find_element_by_xpath(tab_element, "./span[2]")
        tab_label = tab_label_e.text if tab_label_e is not None else ""

        if "all" in tab_label.lower():
            continue

        # click first image item
        first_img = find_element_by_xpath(self, "//*[@class='biz-shim js-lightbox-media-link js-analytics-click']")
        if first_img is None or not tab_label:
            return False

        first_img.click()

        if iterate(self, output):
            print(f"Tab {tab_label} completed.")

        else:
            return False

    return True



def iterate(self, output) -> bool:
    while True:
        if wait_for_element_by_id(self, "lightbox") is None:
            return False

        else:
            parse(self, output)

        next_element = wait_for_element_by_xpath(self, "//*[@id='lightbox-inner']/div[2]/div/div/div[2]/a[2]")

        if next_element is None or next_element.get_attribute("href") is None:
            close_element = wait_for_element_by_xpath(self, "//*[@id='lightbox-inner']/div[1]")
            if close_element is not None:
                close_element.click()
            return True

        else:
            time.sleep(2)

            try:
                next_element.click()

            except WebDriverException:
                return False


def parse(self, file) -> bool:
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
            pic_error_writer.writerow([self.current_url])
            print("Fetching pic error, retry it later...")
            return False

    try:
        tab_label = find_element_by_xpath(
            self,
            "//a[@role='tab'][contains(@class, 'is-selected')]/span[contains(@class, 'tab-link_label')]"
        ).text
        comment = find_element_by_xpath(
            self,
            "//div[contains(@class, 'selected-photo-caption-text')]"
        ).text
        index = find_element_by_xpath(
            self,
            "//span[@class='media-count_current']"
        ).text
        img = wait_for_element_by_xpath(
            self,
            "//img[@class='photo-box-img'][@loading='auto']"
        ).get_attribute("src")
        date = find_element_by_xpath(
            self,
            "//span[contains(@class, 'selected-photo-upload-date')]"
        ).text
    except WebDriverException:
        pic_error_writer.writerow([self.current_url])
        print("Fetching pic error, retry it later...")
        return False

    if img:
        image_name = f"[{tab_label}] {index}"
        image_path = os.path.join(img_folder_path, image_name + ".jpg")
        save_success = save_img(img, image_path)

        if not save_success:
            pic_error_writer.writerow([self.current_url])
            return False

    else:
        pic_error_writer.writerow([self.current_url])
        print("Fetching pic error, retry it later...")
        return False

    try:
        writer = csv.writer(file)
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
        return True
    except OSError:
        pic_error_writer.writerow([self.current_url])
        print("Fetche image failed, try it later...")
        return False


def retry() -> bool:
    global folder_path
    global img_folder_path
    global output_file_path
    global output_file
    global output_writer

    store_error_list = get_input(store_error_file)
    store_error_mutable_list = get_input(store_error_file)
    for biz_url in store_error_list:
        driver.get(biz_url)

        biz_element = find_element_by_xpath(driver, "//link[contains(@href, 'biz_id')]")
        if biz_element is not None:
            ori_link = biz_element.get_attribute("href")
            biz_id = get_param_from_url(ori_link, "biz_id")

        else:
            print("Network error, retry this store later...")
            continue

        folder_path = os.path.join("./Desktop/YelpResults/", biz_id)
        img_folder_path = os.path.join(folder_path, "img")
        output_file_path = os.path.join(folder_path, "manifest.csv")
        output_file = open(output_file_path, "w", encoding="utf-8-sig")

        if not crawl(driver, output_file):
            print("Network error, retry this store later...")
        else:
            print("Business_id {} completed.".format(business_id))
            store_error_mutable_list.remove(biz_url)

        output_file.close()

    pic_error_list = get_input(pic_error_file)
    pic_error_mutable_list = get_input(pic_error_file)
    for img_url in pic_error_list:
        driver.get(img_url)

        biz_element = find_element_by_xpath(driver, "//link[contains(@href, 'biz_id')]")
        if biz_element is not None:
            ori_link = biz_element.get_attribute("href")
            biz_id = get_param_from_url(ori_link, "biz_id")

        else:
            print("Network error, retry this store later...")
            continue

        folder_path = os.path.join("./Desktop/YelpResults/", biz_id)
        img_folder_path = os.path.join(folder_path, "img")
        output_file_path = os.path.join(folder_path, "manifest.csv")
        output_file = open(output_file_path, "w", encoding="utf-8-sig")

        if not parse(driver, output_file):
            print("Network error, retry this store later...")
        else:
            print("Business_id {} completed.".format(business_id))
            pic_error_mutable_list.remove(img_url)

        output_file.close()

    for item in store_error_mutable_list:
        store_error_writer.writerow([item])

    for item in pic_error_mutable_list:
        pic_error_writer.writerow([item])

    return not store_error_mutable_list and not pic_error_mutable_list


if __name__ == '__main__':
    makedir("./Desktop/YelpResults/errors")

    input_path = Path(__file__).with_name("stores.csv")
    input_file = input_path.open(mode="r", encoding="utf-8-sig")
    store_error_file_path = os.path.join("./Desktop/YelpResults/errors", "store_error.csv")
    store_error_file = open(store_error_file_path, "w", encoding="utf-8-sig")
    store_error_writer = csv.writer(store_error_file)
    pic_error_file_path = os.path.join("./Desktop/YelpResults/errors", "pic_error.csv")
    pic_error_file = open(pic_error_file_path, "w", encoding="utf-8-sig")
    pic_error_writer = csv.writer(pic_error_file)

    # do your job
    for business_id in get_input(input_file):
        entrance_url = "https://www.yelp.com/biz_photos/" + business_id
        driver.get(entrance_url)

        cookie_path = Path(__file__).with_name("cookies.pkl")
        if cookie_path.is_file():
            cookies = pickle.load(cookie_path.open(mode="rb"))
            for cookie in cookies:
                driver.add_cookie(cookie)
        else:
            pickle.dump(driver.get_cookies(), cookie_path.open(mode="wb"))

        # prepare dirs
        folder_path = os.path.join("./Desktop/YelpResults/", business_id)
        makedir(folder_path)
        img_folder_path = os.path.join(folder_path, "img")
        makedir(img_folder_path)

        output_file_path = os.path.join(folder_path, "manifest.csv")
        output_file = open(output_file_path, "w", encoding="utf-8-sig")
        output_writer = csv.writer(output_file)
        output_writer.writerow(["category", "img", "comment", "user_id", "is_merchant", "date"])

        if not crawl(driver, output_file):
            store_error_writer.writerow([driver.current_url])
            print("Network error, retry this store later...")
        else:
            print("Business_id {} completed.".format(business_id))

        output_file.close()

    while not retry():
        continue

    print("All retries completed.")

    # deinit
    driver.quit()
    store_error_file.close()
    pic_error_file.close()
