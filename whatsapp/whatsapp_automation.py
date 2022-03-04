import logging
from pprint import pprint
import shutil
import betfairlightweight
import os
from datetime import datetime
import json
from numpy import isin
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
import re
import time
import threading
from filelock import FileLock

HOME = os.getenv("HOME")
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/whatsapp_auto/status.log")  # change to DEBUG to see log all updates


def element_click(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.click()
    return

def element_clickable(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    return

def element_click_send_key(driver,id,data):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.send_keys(data)
    return

def view_element(driver,element):
    driver.execute_script("arguments[0].scrollIntoView();",element)

def element_present(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.presence_of_element_located((By.XPATH, id))
              )
    return 

HOME = os.getenv("HOME")
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/whatsapp/status.log")  # change to DEBUG to see log all updates

def send_good_morning_msg():
    firefox_path = f"{HOME}/webdriver/geckodriver"
    firefox_option = Options()
    firefox_option.add_argument("--headless")
    firefox_option.add_argument("--window-size=1920,1080")
    profile_path = f"{HOME}/browser_profiles/firefox"

    firefox_option.profile = profile_path
    
    
    s=Service(executable_path=firefox_path,log_path=os.devnull)

    if selenium.__version__ == "3.14.0" :
        driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                                   service_log_path=os.devnull)
    else:
        driver = webdriver.Firefox(options=firefox_option,service=s)

    driver.get("https://web.whatsapp.com/")

    target_list = ["appa","amma","Atte","Archana"]

    for target in target_list:
        element_click_send_key(driver,'//div[@title="Search input textbox"]',target)

        if selenium.__version__ == "3.14.0" :
            chat_list = driver.find_elements_by_xpath('//div[@class="_3m_Xw"]')
        else:
            chat_list = driver.find_elements(By.XPATH,'//div[@class="_3m_Xw"]')

        for chat in chat_list:
            try:
                appa_element = chat.find_element(By.XPATH,f".//span[@title='{target}']")
                view_element(driver,chat)
                appa_element.click()
                break
            except:
                continue

        element_click_send_key(driver,".//div[@title='Type a message']","Goood Morning")
        element_click(driver,".//button[.//span[@data-icon='send']]")
    
    logging.info("Good morning message sent")
    driver.quit()

send_good_morning_msg()