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
from selenium.webdriver.firefox.service import Service, service
import keyring
import time


def element_view(driver,element):
    driver.execute_script("arguments[0].scrollIntoView();",element)

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

def open_driver(exec_path):
    firefox_option = Options()
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")

    s=Service(executable_path=exec_path,log_path=os.devnull)

    driver = webdriver.Firefox(options=firefox_option,service=s)
    return(driver)

def open_driver_headless(exec_path):
    firefox_option = Options()
    firefox_option.add_argument("--headless")
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")

    s=Service(executable_path=exec_path,log_path=os.devnull)

    driver = webdriver.Firefox(options=firefox_option,service=s)
    return(driver)

def splitwise_login(driver):
    driver.get("https://www.splitwise.com/login")
    gmail_id = keyring.get_password('system','my_gmail_id')
    gmail_pass = keyring.get_password('system','my_gmail_pass')
    element_click_send_key(driver,"//input[@type='email']",gmail_id)
    element_click_send_key(driver,"//input[@type='password']",gmail_pass)
    element_click(driver,"//input[@type='submit']")
    time.sleep(4)
    element_click(driver,"//a[./span='Archana G Upadhya']")
    pass

def add_expense(driver,name,amount,i_paid):
    element_click(driver,"//a[contains(text(),'Add an expense')]")
    element_click_send_key(driver,"//input[@class='description']",name)
    element_click_send_key(driver,"//input[@class='cost']",amount)
    if not i_paid:
        element_click(driver,"//a[@class='payer']")
        element_click(driver,"//li[@class='main_payer ']")
        time.sleep(2)
    
    element_click(driver,"//button[contains(text(),'Save')]")


