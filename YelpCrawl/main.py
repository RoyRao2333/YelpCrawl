import os
import csv
import time
import re
import pickle
import requests
import shutil
import ujson
from requests.exceptions import RequestException, ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, parse_qsl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from pathlib import Path


# init driver
option = webdriver.ChromeOptions()
option.headless = True
driver = webdriver.Chrome(options=option)


def get_api_response(_business_id: str, _tab: str, _start_index: int):
    api_url = "https://www.yelp.com/biz_photos/get_media_slice/" + _business_id
    params = {
        "tab": _tab,
        "get_local_ads": 1,
        "start": _start_index,
        "dir": "f"
    }
    headers = {
        "cookie": 'hl=en_US; wdi=1|0BCD290FF7E6CE4D|0x1.8876f26a29436p+30|b040b424a6b4c121; _ga=GA1.2.0BCD290FF7E6CE4D; _gcl_au=1.1.895274846.1646131350; _fbp=fb.1.1646131351849.2071739835; __qca=P0-406397092-1646131358352; g_state={"i_p":1646450901916,"i_l":2}; qntcst=D; bse=a2a021bd9dd9485c92f06836f664d380; _gid=GA1.2.1045250838.1646896722; recentlocations=; location={"unformatted":+"Las+Vegas,+NV",+"max_latitude":+36.33753626472455,+"provenance":+"YELP_GEOCODING_ENGINE",+"state":+"NV",+"address1":+"",+"max_longitude":+-114.911930734375,+"address2":+"",+"accuracy":+4,+"longitude":+-115.13986054589839,+"location_type":+"locality",+"country":+"US",+"min_latitude":+35.95598271139048,+"display":+"Las+Vegas,+NV",+"min_longitude":+-115.35955061132813,+"latitude":+36.169631736226485,+"county":+"Clark+County",+"parent_id":+995,+"zip":+"",+"city":+"Las+Vegas",+"place_id":+"1242",+"address3":+"",+"borough":+"",+"isGoogleHood":+false,+"language":+null,+"neighborhood":+"",+"polygons":+null,+"usingDefaultZip":+false,+"confident":+null}; _uetsid=b69e53c0a04d11ec93f2a32999083266; _uetvid=4c20b390994c11ecba1abb10331f4c56; _clck=1wbeoa0|1|ezn|0; _clsk=1h8kglq|1646901627573|1|0|j.clarity.ms/collect; xcj=1|cf9XdjLupPzjW5eyyR2v8-3EsBmQVAOJqjzuxI76cfo; _gat_global=1; OptanonConsent=isIABGlobal=false&datestamp=Thu+Mar+10+2022+16:42:10+GMT+0800+(China+Standard+Time)&version=6.10.0&hosts=&consentId=b169c059-688e-4aa5-a74a-36c1a0ecb01d&interactionCount=1&landingPath=NotLandingPage&groups=BG10:1,C0003:1,C0002:1,C0001:1,C0004:1&AwaitingReconsent=false; pid=6528f008fd967298',
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56",
        "referer": f"https://www.yelp.com/biz_photos/{_business_id}",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
        "sec-ch-ua-platform": '"macOS"',
        "x-requested-with": "XMLHttpRequest",
    }

    try:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
        session.mount('https://', adapter)
        print("Request api succeeded.")
        return session.get(api_url, params=params, headers=headers, timeout=2)

    except (RequestException, ConnectionError) as error:
        print(f"Request api failed with error: {type(error)}: {error}.")
        return False


def find_element_by_xpath(self, xpath):
    try:
        return self.find_element(by=By.XPATH, value=xpath)

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return None


def find_elements_by_xpath(self, xpath):
    try:
        return self.find_elements(by=By.XPATH, value=xpath)

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return list()


def find_element_by_id(self, value):
    try:
        return self.find_elements(by=By.ID, value=value)

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return None


def wait_for_element_by_id(self, value):
    try:
        return WebDriverWait(self, 10).until(ec.presence_of_element_located((By.ID, value)))

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return None


def wait_for_element_by_xpath(self, value):
    try:
        return WebDriverWait(self, 10).until(ec.presence_of_element_located((By.XPATH, value)))

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return None


def find_elements_by_class_name(self, class_name):
    try:
        return self.find_elements(by=By.CLASS_NAME, value=class_name)

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return list()


def get_attribute(self: WebElement, _attr: str):
    try:
        return self.get_attribute(_attr)

    except WebDriverException as error:
        print(f"{type(error)}: {error}")
        return None


def makedir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)


def save_img(img_url, path) -> bool:
    try:
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=0.5))
        session.mount('https://', adapter)
        response = session.get(img_url, stream=True)

    except (RequestException, ConnectionError) as error:
        print(f"Image fetch failed with error {type(error)}: {error}.")
        return False

    else:
        if response.status_code == 200:
            response.raw.decode_content = True

        else:
            print('Image Couldn\'t be retreived')
            return False

    try:
        with open(path, 'wb') as img_file:
            shutil.copyfileobj(response.raw, img_file)
        return True

    except OSError as error:
        print(f"Image save failed with error {type(error)}: {error}.")
        return False


def get_param_from_url(url: str, key: str):
    try:
        parsed = urlparse(url)
        params = dict(parse_qsl(parsed.query))
        return params[key] if params[key] is not None else ""

    except ValueError as error:
        print(f"{type(error)}: {error}")
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
        print("Site is not completely loaded. Retry it again later...")
        return False

    for tab_element in tab_list:
        try:
            tab_element.click()
        except WebDriverException as error:
            print(f"Selecting tab failed with error {type(error)}: {error}. Trying to expand sections...")
            try:
                find_element_by_xpath(self, "//div[contains(@class, 'paged-scroll-container_arrow-right')]").click()
                time.sleep(2)
                tab_element.click()
            except (WebDriverException, ValueError) as error:
                print(f"Expanding tab failed with error {type(error)}: {error}...")
                return False

        tab_label = find_element_by_xpath(tab_element, "./span[2]")

        if tab_label:
            tab_label_text = tab_label.text

        else:
            print("Tab is not completely loaded. Retry it again later...")
            continue

        tab_name = get_attribute(tab_element, "data-media-tab-label")

        if not tab_name or "all" in tab_label_text.lower():
            continue

        parse(self, tab_name, output)

    return True


def parse(self, _tab_name, output):
    _start_index = 0
    while True:
        time.sleep(2)
        _response = get_api_response(business_id, _tab_name, _start_index)
        if not _response:
            break

        try:
            _json_data = _response.json()

        except (UnicodeDecodeError, RequestException) as error:
            print(f"{type(error)}: {error}")
            continue

        for _media_item in _json_data["media"]:
            if _media_item["media_type"] != "photo":
                continue

            _item_index = _media_item["index"]
            _media_data = _media_item["media_data"]
            _img_src = _media_data["url"]
            _date_posted = _media_data["timeUploaded"]
            _comment = _media_data["caption"]
            _user_data = _media_data["user"]

            if _user_data:
                _user_name = _user_data["displayName"]
                _is_merchant = "No"

            else:
                _merchant_name = find_element_by_xpath(
                    self,
                    "//a[@data-analytics-label='biz-name']/span"
                )
                _user_name = _merchant_name.text if _merchant_name else "business owner"
                _is_merchant = "Yes"

            if _img_src:
                image_name = f"[{_tab_name}] {_item_index}"
                image_path = os.path.join(img_folder_path, image_name + ".jpg")
                save_success = save_img(_img_src, image_path)

                if not save_success:
                    pic_error_writer.writerow([self.current_url])
                    print("Saving pic failed, retry it later...")
                    continue

            else:
                pic_error_writer.writerow([self.current_url])
                print(f"Fetching pic failed, retry it later...")
                continue

            try:
                writer = csv.writer(output)
                writer.writerow([
                    _tab_name,
                    image_name,
                    _comment,
                    _user_name,
                    _is_merchant,
                    _date_posted
                ])
                output.flush()
                print("Fetched " + image_name)

            except OSError as error:
                pic_error_writer.writerow([self.current_url])
                print(f"Writing output failed with error {type(error)}: {error}, try it later...")

        _start_index += 30

    print(f"Tab {_tab_name} completed.")


def retry():
    global folder_path
    global img_folder_path
    global output_file_path
    global output_file
    global output_writer


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

        success = crawl(driver, output_file)
        if not success:
            store_error_writer.writerow([driver.current_url])
            print("Network error, retry this store later...")
        else:
            print("Business_id {} completed.".format(business_id))

        output_file.close()

    # while not retry():
    #     continue
    #
    # print("All retries completed.")

    # deinit
    driver.quit()
    store_error_file.close()
    pic_error_file.close()
