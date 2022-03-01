import os
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

def find_element_by_xpath(self, xpath):
    return self.find_element(by=By.XPATH, value=xpath)


def mkdir(path):
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)
        print("---  new folder...  ---")

    else:
        print("---  There is this folder!  ---")

def get_input():
    input_file = open(os.getcwd() + "/stores.csv", mode="r", encoding="utf-8-sig")
    csv_reader = csv.reader(input_file)
    input_list = list()

    for line in csv_reader:
        item = line[0]
        if item is not None and isinstance(item, str):
            input_list.append(item)

    return input_list

# def crawl(self, file):


def parse(self, file):
    writer = csv.writer(file)
    results = find_element_by_xpath("")
    for item in results:
        writer.writerow(["", ""])

    file.flush()

if __name__ == '__main__':
    service = Service("/usr/local/bin/msedgedriver")
    service.start()
    driver = webdriver.Remote(service.service_url)
    driver.get("https://www.baidu.com/")

    output_file = open(os.getcwd() + "/results" + "/manifest.csv", "w", encoding="utf-8-sig")
    image_folder = os.getcwd() + "/results/img/"

    csv_writer = csv.writer(output_file)
    csv_writer.writerow(["img", "comment", "user", "isMerchant"])

    crawl(driver, output_file)

    output_file.close()
    driver.quit()