import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from shutil import which
import codecs

firefox_path = "C:\Personal\studies\geckodriver.exe"

firefox_option = Options()
firefox_option.add_argument("--headless")
firefox_option.add_argument("--window-size=1920,1080")

driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option)

driver.get("https://amazon.co.uk")

search_input = driver.find_element_by_xpath("//input[@id='twotabsearchtextbox']")
search_input.send_keys("aaa batteries")

search_btn = driver.find_element_by_xpath("//input[@id='nav-search-submit-button']")
search_btn.click()

driver.implicitly_wait(2)
page_results = Selector(text=driver.page_source)

results = page_results.xpath("//div[@class='sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20']")
for result in results:
    result_title = result.xpath(".//span[@class='a-size-medium a-color-base a-text-normal']/text()").get()
    result_price = result.xpath(".//span[@class='a-offscreen']/text()").get()
    if result_price:
        print(f"Titel : {result_title} Price : {result_price}")

next_page=page_results.xpath("//li[@class='a-last']/a/@href").get()

driver.get(f"https://amazon.co.uk{next_page}")
print("Display page 2 results")
search_input = driver.find_element_by_xpath("//input[@id='twotabsearchtextbox']")
search_input.send_keys("aaa batteries")

search_btn = driver.find_element_by_xpath("//input[@id='nav-search-submit-button']")
search_btn.click()

driver.implicitly_wait(2)
page_results = Selector(text=driver.page_source)

results = page_results.xpath("//div[@class='sg-col sg-col-4-of-12 sg-col-8-of-16 sg-col-12-of-20']")
for result in results:
    result_title = result.xpath(".//span[@class='a-size-medium a-color-base a-text-normal']/text()").get()
    result_price = result.xpath(".//span[@class='a-offscreen']/text()").get()
    if result_price:
        print(f"Titel : {result_title} Price : {result_price}")

driver.quit()
