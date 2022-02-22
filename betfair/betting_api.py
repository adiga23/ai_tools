import logging
from pprint import pprint
import betfairlightweight
import os
from datetime import timedelta
from datetime import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import selenium
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
import re


HOME = os.getenv("HOME")

# def open_driver():
#     HOME = os.getenv("HOME")
#     firefox_path = f"{HOME}/webdriver/geckodriver"
#     firefox_option = Options()
#     #firefox_option.add_argument("--headless")
#     firefox_option.add_argument("--window-size=1920,1080")
#     #firefox_option.add_argument("--incognito")
#     if selenium.__version__ == "3.14.0":
#         driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
#                                    service_log_path=os.devnull)
#     else:
#         s=Service(executable_path=firefox_path,log_path=os.devnull)
#         driver = webdriver.Firefox(options=firefox_option,service=s)
#     return(driver)

# def element_click(driver,id):
#     element = WebDriverWait(driver, 30).until(
#               EC.element_to_be_clickable((By.XPATH, id))
#               )
#     element.click()
#     return

# def element_click_send_key(driver,id,data):
#     element = WebDriverWait(driver, 30).until(
#               EC.element_to_be_clickable((By.XPATH, id))
#               )
#     element.send_keys(data)
#     return

# driver = open_driver()

# driver.get("https://www.google.com")

# try:
#     element_click(driver,'//div[contains(text(),"I agree")]')
# except:
#     pass

# driver.get("https://www.google.com")

# element_click_send_key(driver,'//input[@title="Search"]',"De Minaur v McDonald")
# search_btn = driver.find_elements(By.XPATH,"//input[@value='Google Search']")
# search_btn[1].click()

# exit()

def send_email(to_email,subject,msg):
    HOME = os.getenv("HOME")
    with open(f"{HOME}/pass_info.json",'r') as f:
        pass_info = json.load(f)
    python_account = pass_info["pygmail"]["username"]
    python_password = pass_info["pygmail"]["password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = python_account
    message["To"] = to_email
    message.attach(MIMEText(msg,"html"))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.ehlo()
        server.login(python_account,python_password)
        server.sendmail(python_account,to_email,message.as_string())
        server.close()
        success = True
    except:
        success = False
    return(success)

# setup logging
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/betting/status.log")  # change to DEBUG to see log all updates
    

class Odds():
    def __init__(self):
        self.price = 0
        self.size = 0

    def todict(self):
        return({"price" : self.price,
                "size"  : self.size})

    def fromdict(self,in_dict):
        self.price = in_dict["price"]
        self.size = in_dict["size"]

class Runner():
    def __init__(self):
        self.status = "ACTIVE"
        self.selection_id = ""
        self.odds = []

    def todict(self):
        odds_list = []
        for odd in self.odds:
            odds_list.append(odd.todict().copy())
        return({"status"       : self.status,
                "selection_id" : self.selection_id,
                "odds"         : odds_list})

    def fromdict(self,in_dict):
        self.status = in_dict["status"]
        self.selection_id = in_dict["selection_id"]
        odds_list = []
        for odd_dict in in_dict["odds"]:
            newodd = Odds()
            newodd.fromdict(odd_dict)
            odds_list.append(newodd)
        self.odds = odds_list

class Market():
    def __init__(self):
        self.status = "OPEN"
        self.players = []
        self.runners = []
    
    def todict(self):
        runners_list = []
        for runner in self.runners:
            runners_list.append(runner.todict().copy())
        local_dict = {"status"  : self.status,
                      "players" : self.players,
                      "runners" : runners_list}
        return(local_dict)

    def fromdict(self,in_dict):
        self.status = in_dict["status"]
        self.players = in_dict["players"]
        runners_list = []
        for runner_dict in in_dict["runners"]:
            new_runner = Runner()
            new_runner.fromdict(runner_dict)
            runners_list.append(new_runner)
        self.runners=runners_list




def get_latest_odds():
    HOME = os.getenv("HOME")
    odds_info_dict = {}
    with open(f"{HOME}/pass_info.json","r") as f:
        pass_info = json.load(f)
    # create trading instance
    trading = betfairlightweight.APIClient(pass_info["betfair"]["username"], pass_info["betfair"]["password"] , app_key=pass_info["betfair"]["app_key"],certs=f'{HOME}/login_tokens/betfair')

    # login
    # try:
    trading.login()




    # Grab all event type ids. This will return a list which we will iterate over to print out the id and the name of the sport
    tennis_market_filter = betfairlightweight.filters.market_filter(text_query="Tennis")
    event_types = trading.betting.list_event_types(filter=tennis_market_filter)
    tennis_id = event_types[0].event_type.id
    tennis_event_filter = betfairlightweight.filters.market_filter(event_type_ids=[tennis_id],in_play_only=True)
    onging_tennis_events = trading.betting.list_events(filter=tennis_event_filter)
    market_id_list = []
    for tennis_event in onging_tennis_events:
        p1 = re.sub(r"(.*?) v .*",r"\1",tennis_event.event.name)
        p2 = re.sub(r".*? v (.*)",r"\1",tennis_event.event.name)
        id = tennis_event.event.id
        market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=[id])
        market_catalogues = trading.betting.list_market_catalogue(
                                filter=market_catalogue_filter,
                                max_results='100'
                            )
        
        for market in market_catalogues:
            market_id = market.market_id
            market_name = market.market_name
            if market_name in ["Match Odds","Set 1 Winner","Set 2 Winner","Set 3 Winner","Set 4 Winner","Set 5 Winner"]:
                market_id_list.append(market_id)
                odds_info_dict.update({market_id:{"players" : [p1,p2],
                                                  "market_name" : market_name}})

    price_filter = betfairlightweight.filters.price_projection(
                            price_data=['EX_BEST_OFFERS']
                        )
    market_book = trading.betting.list_market_book(market_ids=market_id_list,
                                                   price_projection=price_filter)
    for market in market_book:
        status = market.status
        market_id = market.market_id
        runner_list = []
        for runner in market.runners:
            selection_id = runner.selection_id
            runner_status = runner.status
            odds_data_list = []
            for odds_data in runner.ex.available_to_back:
                odds_data_list.append({"price" : odds_data.price,
                                       "size"  : odds_data.size})
            runner_dict = {"selection_id" : selection_id,
                           "status"       : runner_status,
                           "odds"         : odds_data_list}
            runner_list.append(runner_dict.copy())
        odds_info_dict[market_id].update({"status"  : status,
                                          "runners" : runner_list})
    pprint(odds_info_dict)
        
    # except:
    #     odds_info_dict = {}
    #     pass

    try:
        trading.logout()
    except:
        pass

    return(odds_info_dict)

latest_odds = get_latest_odds()

exit()




pprint(market_book)
pprint(vars(market_book[0]))

#betfairlightweight.filters.place_instruction(order)
try:
    trading.logout()
except:
    pass

# try:
#     driver.quit()
# except:
#     pass

#send_email("adiga23@gmail.com",f"Database Download interrupted {datetime.now().strftime('%d/%m/%Y')}",f"Downloaded till {curr_date.strftime('%d/%m/%Y')}")
