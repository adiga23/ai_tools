from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service, service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from datetime import date, datetime
import json
import os
import keyring
from pprint import pprint
import time

def view_element(driver,element):
    driver.execute_script("arguments[0].scrollIntoView();",element)

def get_element_src(element):
    return(element.get_attribute('innerHTML'))

def element_click_send_key(driver,id,data):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.send_keys(data)
    return

def element_view(element):
    element.execute_script("arguments[0].scrollIntoView();",element)

def element_clikable(element):
    temp_element = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(element)
                   )
    return

def element_present(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.presence_of_element_located((By.XPATH, id))
              )
    return   

def element_double_click(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    #Double-click
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.double_click(element)
    actions.perform()

def element_click(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.click()
    return

def open_firefox_driver(exec_path):
    firefox_option = Options()
    firefox_option.add_argument("--headless")
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")

    s=Service(executable_path=exec_path,log_path=os.devnull)

    driver = webdriver.Firefox(options=firefox_option,service=s)
    return(driver)

def open_firefox_driver_gui(exec_path):
    firefox_option = Options()
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")

    s=Service(executable_path=exec_path,log_path=os.devnull)

    driver = webdriver.Firefox(options=firefox_option,service=s)
    return(driver)

## Select element from the scroll list
select = Select(driver.find_element_by_id('fruits01'))

# select by visible text
select.select_by_visible_text('Banana')

# select by value 
select.select_by_value('1')

## switch frame

driver.switch_to.frame(<num>)

## Older version code :
firefox_path = f"{HOME}/webdriver/geckodriver"
firefox_option = Options()
#firefox_option.add_argument("--headless")
firefox_option.add_argument("--window-size=1920,1080")
firefox_option.add_argument("--incognito")
s=Service(executable_path=firefox_path,log_path=os.devnull)
#driver = webdriver.Firefox(options=firefox_option,service=s)
driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                           service_log_path=os.devnull)
driver.get("https://outlook.office365.com/owa/calendar/CambridgeGym@arm.com/bookings/")
a=input("Adiga")
driver.quit()

## Newer version of code with deubbing
         ## open chrome using
        chrome_path = f"{HOME}/webdriver/chromedriver"
        chrome_option = Options()
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        s=Service(executable_path=chrome_path,log_path=os.devnull)
        driver = webdriver.Chrome(options=chrome_option,service=s)

some code for old and new

if selenium.__version__ == "3.14.0" :
    driver.find_element_by_xpath(id)
else:
    driver.find_element(By.XPATH,id)
