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
import time


HOME = os.getenv("HOME")
# with open(f"{HOME}/pass_info.json","r") as f:
#     pass_info = json.load(f)
# trading = betfairlightweight.APIClient(pass_info["betfair"]["username"], pass_info["betfair"]["password"] , app_key=pass_info["betfair"]["app_key"],certs=f'{HOME}/login_tokens/betfair')
# trading.login()
# market_id_list = ["1.195133262"]
# price_filter = betfairlightweight.filters.price_projection(
#                                 price_data=['EX_BEST_OFFERS']
#                 )
# market_book = trading.betting.list_market_book(market_ids=market_id_list,
#                                                price_projection=price_filter)

# trading.logout()

# pprint(vars(market_book[0]))

# exit()

# setup logging
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/daily_tennis_data/status.log")  # change to DEBUG to see log all updates

def get_latest_odds(daily_info):
    HOME = os.getenv("HOME")
    odds_info_dict = {}
    with open(f"{HOME}/pass_info.json","r") as f:
        pass_info = json.load(f)
    # create trading instance
    trading = betfairlightweight.APIClient(pass_info["betfair"]["username"], pass_info["betfair"]["password"] , app_key=pass_info["betfair"]["app_key"],certs=f'{HOME}/login_tokens/betfair')

    # login
    try:
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
                                    max_results='1000'
                                )
            
            for market in market_catalogues:
                market_id = market.market_id
                market_name = market.market_name
                if market_name in ["Match Odds","Set 1 Winner","Set 2 Winner","Set 3 Winner","Set 4 Winner","Set 5 Winner"]:
                    market_id_list.append(market_id)
                    odds_info_dict.update({market_id:{"players" : [p1,p2],
                                                    "market_name" : market_name}})

        for market_id in daily_info.keys():
            if market_id not in market_id_list:
                if daily_info[market_id]["status"] != "CLOSED":
                    market_id_list.append(market_id)

        pprint(market_id_list)
        price_filter = betfairlightweight.filters.price_projection(
                                price_data=['EX_BEST_OFFERS']
                            )
        market_book = trading.betting.list_market_book(market_ids=market_id_list,
                                                    price_projection=price_filter)

        for market in market_book:
            status = market.status
            market_id = market.market_id
            not_valid_market_id = (market_id not in odds_info_dict.keys()) and \
                                  (market_id not in daily_info.keys())
            if not_valid_market_id :
                continue
            if market_id not in odds_info_dict.keys():
                odds_info_dict.update({market_id:{"players" : daily_info[market_id]["players"].copy(),
                                                  "market_name" : daily_info[market_id]["market_name"]}})

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
 
    except:
        odds_info_dict = {}
        pass

    try:
        trading.logout()
    except:
        pass

    return(odds_info_dict)

def update_odds_info(daily_info,latest_odds):
    for key,value in latest_odds.items():
        if key in daily_info.keys():
            daily_info[key]["status"] = value["status"]
            daily_info[key]["odds_list"].append(value["runners"].copy())
        else:
            # if value["status"] == "OPEN":
            if True:
                odds_list = [value["runners"].copy()]

                daily_info_value = {"market_name" : value["market_name"],
                                    "players"     : value["players"],
                                    "status"      : value["status"],
                                    "odds_list"   : odds_list}
                daily_info.update({key:daily_info_value})
    pass

def get_live_scores():
    HOME = os.getenv("HOME")
    firefox_path = f"{HOME}/webdriver/geckodriver"
    firefox_option = Options()
    #firefox_option.add_argument("--headless")
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")
    s=Service(executable_path=firefox_path,log_path=os.devnull)
    if selenium.__version__ == "3.14.0" :
        driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                                   service_log_path=os.devnull)
    else:
        driver = webdriver.Firefox(options=firefox_option,service=s)

    driver.get("https://www.betfair.com/sport/inplay")
    
get_live_scores()
exit()
with open("temp.json","r") as f:
    daily_info = json.load(f)

a = datetime.now()
for i in range(0,1):
    pprint(f"In iteration {i}")
    latest_odds = get_latest_odds(daily_info)
    update_odds_info(daily_info,latest_odds)
    time.sleep(5)
b = datetime.now()
pprint(daily_info)
c = b - a

with open("temp.json","w") as f:
    json.dump(daily_info,f)
pprint(f"seconds : {c.seconds} micro_seconds : {c.microseconds}")


