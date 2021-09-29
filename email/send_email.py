import scrapy
import os
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import time

if os.name == "posix":
    #mac path
    firefox_path = "/Users/raga/python_scripts/geckodriver"
else:
    firefox_path = "C:\Personal\studies\geckodriver.exe"

def element_click_send_key(driver,id,data):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.send_keys(data)
    return

def element_click(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.click()
    return

def element_present(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.presence_of_element_located((By.XPATH, id))
              )
    return

def get_next_src(driver,id):
    element_present(driver,id)
    page_source = Selector(text=driver.page_source)
    next_src = page_source.xpath(f"{id}/@href").get()
    driver.get(next_src)

def gmail_login(driver):
    ## Log into gmail
    driver.get("https://www.gmail.com")
    ## Enter Username
    element_click_send_key(driver,"//input[@id='identifierId']","tpython381")
    ## Click next
    element_click(driver,"//div[@id='identifierNext']")
    ## Enter Password
    element_click_send_key(driver,"//input[@name='password']","obsessed_worker")
    time.sleep(2)
    ## Click Next
    element_click(driver,"//div[@id='passwordNext']")

def compose_email(driver,to,subject,message):
    ## Click on compose
    element_click(driver,"//div[text()='Compose']")
    ## email id of the receiver
    element_click_send_key(driver,"//textarea[@name='to']",to)
    ## enter the subject
    element_click_send_key(driver,"//input[@name='subjectbox']",subject)
    ## enter the message
    element_click_send_key(driver,"//div[@class='Am Al editable LW-avf tS-tW']",message)
    ## Click send
    element_click(driver,"//div[text()='Send']")
    ## Wait for the message to be sent
    element_present(driver,"//span[text()='Message sent.']")

def logout(driver):
    ## Click on the account
    element_click(driver,"//a[contains(@aria-label,'Google Account:') and @role='button']")
    ## get the src to logout
    get_next_src(driver,"//a[text()='Sign out']")
    ## wait for the logout
    element_present(driver,"//div[text()='Use another account']")

firefox_option = Options()
firefox_option.add_argument("--headless")
firefox_option.add_argument("--window-size=1920,1080")
firefox_option.add_argument("--incognito")

driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                           service_log_path=os.devnull)

print("Logging into GMAIL .....")
gmail_login(driver)
to = "adiga23@gmail.com"
subject = f"Python {datetime.datetime.now()}"
message = "Sending email from python script"
print("Sending message ......")
compose_email(driver,to,subject,message)
print("Logging out.....")
logout(driver)
driver.quit()
