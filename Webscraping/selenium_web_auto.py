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

#driver = webdriver.Firefox(executable_path=firefox_path)
driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option)

driver.get("https://duckduckgo.com")

search_input = driver.find_element_by_xpath("//input[@id='search_form_input_homepage']")
search_input.send_keys("My user agent")

search_btn = driver.find_element_by_xpath("//input[@id='search_button_homepage']")
search_btn.click()

driver.implicitly_wait(2)
page_results = Selector(text=driver.page_source)

results = page_results.xpath("//div[@class='result__body links_main links_deep']")
for result in results:
    result_head = result.xpath(".//a[@class='result__a js-result-title-link']/text()").get()
    result_descr = result.xpath(".//div[@class='result__snippet js-result-snippet']/node()").extract()
    print(result_descr)
    print(result_head)

next_page=page_results.xpath("//li[@class='a-last']/a/@href")
driver.quit()
