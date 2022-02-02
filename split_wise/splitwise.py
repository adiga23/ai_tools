import scrapy
import os
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
import time
from selenium.webdriver.chrome.service import Service, service
import sys
import json
from filelock import FileLock
import logging
HOME = os.getenv("HOME")
logging.basicConfig(filename=f"{HOME}/script_stat/splitwise/status.log",filemode="w",level=logging.INFO)


## This script to be run on raspberry PI board
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
    chrome_option = Options()
    chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    s=Service(executable_path=exec_path,log_path=os.devnull)

    driver = webdriver.Chrome(options=chrome_option,service=s)
    return(driver)

def splitwise_login(driver):
    HOME = os.getenv("HOME")
    driver.get("https://www.splitwise.com/login")
    with open(f"{HOME}/pass_info.json","r") as f:
        pass_info = json.load(f)
    gmail_id = pass_info["mygmail"]["username"]
    gmail_pass = pass_info["mygmail"]["password"]
    try:
        element_click_send_key(driver,"//input[@type='email']",gmail_id)
        element_click_send_key(driver,"//input[@type='password']",gmail_pass)
        element_click(driver,"//input[@type='submit']")
    except:
        pass

    time.sleep(4)
    try:
        element_click(driver,"//a[./div='Archana G Upadhya']")
    except:
        pass
    try:
        element_click(driver,"//a[./span='Archana G Upadhya']")
    except:
        pass
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

def first_weekday_of_month():
    curr_date = datetime(datetime.now().year,datetime.now().month,1)
    delta = timedelta(days=1)
    is_weekday = curr_date.weekday() in [0,1,2,3,4]
    while not is_weekday:
        curr_date += delta
        is_weekday = curr_date.weekday() in [0,1,2,3,4]
    return(curr_date.day)

curr_date = datetime.now()
now = datetime.now().strftime('%d/%m/%Y:%H:%M')
with open(f"{HOME}/script_stat/splitwise/basic_expense.json","r") as f:
    expenses = json.load(f)

with open(f"{HOME}/script_stat/splitwise/last_update.txt","r") as f:
    last_update_date = f.read()
    last_update_date = datetime.strptime(last_update_date.rstrip('\n'),'%d/%m/%Y')


lock = FileLock(f"{HOME}/serialise")
lock.acquire()
logging.info(f"Splitwise Lock acquired at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
driver_path = f"{HOME}/webdriver/chromedriver"

if curr_date.month != last_update_date.month:
    update_success = False
    try:
        driver = open_driver(driver_path)
        splitwise_login(driver)
        for key in expenses.keys():
            time.sleep(4)
            add_expense(driver,key,expenses[key]['amount'],(expenses[key]['i_paid'] == 1))
        logging.info(f"{now} : updated the expenses")
        update_success = True
    except:
        logging.info(f"{now} : Fault in accessing splitwise")

    if update_success:
        f=open(f"{HOME}/script_stat/splitwise/last_update.txt",'w')
        f.write(datetime.now().strftime('%d/%m/%Y'))
        f.close()
else:
    logging.info(f"{now} : Not updating the expenses")

lock.release()

logging.info(f"Splitwise Lock released at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
