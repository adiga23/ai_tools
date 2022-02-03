from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service, service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date, datetime
import json
import os
import keyring
from pprint import pprint
import time
from filelock import FileLock
import threading
import logging
HOME = os.getenv("HOME")
logging.basicConfig(filename=f"{HOME}/script_stat/gym_booking/status.log",filemode="w",level=logging.INFO)

def element_click_send_key(driver,id,data):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.send_keys(data)
    return

def element_view(element):
    driver.execute_script("arguments[0].scrollIntoView();",element)

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

def element_click(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.element_to_be_clickable((By.XPATH, id))
              )
    element.click()
    return

def find_time_element(input_element,text):
    list_elements = input_element.find_elements(By.XPATH,".//li")
    output_element = None
    for element in list_elements:
        text_element = element.find_element(By.XPATH,".//span")
        if text_element.text == text:
            output_element = element
            break
    return(output_element)

booking_exempt = False
curr_date = datetime.now()
f=open(f"{HOME}/script_stat/gym_booking/last_update.txt",'r')
last_update_date = f.read()
last_update_date = datetime.strptime(last_update_date.rstrip('\n'),'%d/%m/%Y')
f.close()


lock = FileLock(f"{HOME}/serialise")
lock.acquire()

logging.info(f"Lock acquired at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")

if curr_date.day == last_update_date.day:
    booking_exempt = True
try:
    if not booking_exempt:
        firefox_path = f"{HOME}/webdriver/geckodriver"
        firefox_option = Options()
        firefox_option.add_argument("--headless")
        firefox_option.add_argument("--window-size=1920,1080")
        firefox_option.add_argument("--incognito")
        s=Service(executable_path=firefox_path,log_path=os.devnull)
        driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                                   service_log_path=os.devnull)

        f = open(f"{HOME}/script_stat/gym_booking/user_info.json","r")
        user_info = json.load(f)
        f.close()
        time_slots = ["11:00","12:00","13:00"]
        for key in user_info.keys():
            name = user_info[key]["name"]
            email_id = user_info[key]["email_id"]
            for time_slot in time_slots:
                driver.get("https://outlook.office365.com/owa/calendar/CambridgeGym@arm.com/bookings/")
                element_click(driver,"//label[@for='service_2']")
                element_present(driver,"//div[@class='focusable timePicker']")
                time_element = driver.find_element(By.XPATH,"//div[@class='focusable timePicker']")
                element_view(time_element)
                time_element = find_time_element(time_element,time_slot)
                if time_element is not None:
                    element_clikable(time_element)
                    time_element.click()
                    element_click_send_key(driver,"//input[@placeholder='Name']",name)
                    element_click_send_key(driver,"//input[@placeholder='Email']",email_id)
                    element_click(driver,"//button[@class='bookButton']")
                    now = datetime.now()
                    now = now.strftime('%d/%m/%Y:%H:%M')
                    logging.info(f"{now} Booked Gym for {name} slot {time_slot}")
        f=open(f"{HOME}/script_stat/gym_booking/last_update.txt",'w')
        f.write(datetime.now().strftime('%d/%m/%Y'))
        f.close()
    else:
        now = datetime.now()
        now = now.strftime('%d/%m/%Y:%H:%M')
        logging.info(f"{now} Booking Gym was exempted, so not booking")
except:
    now = datetime.now()
    now = now.strftime('%d/%m/%Y:%H:%M')
    logging.info(f"{now} Some problem occurred while booking")

try:
    driver.quit()
except:
    pass
lock.release()
logging.info(f"Lock released at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
