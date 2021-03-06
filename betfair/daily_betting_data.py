import logging
from pprint import pprint
import betfairlightweight
import os
from datetime import datetime
import json
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
import shutil

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

def view_element(driver,element):
    driver.execute_script("arguments[0].scrollIntoView();",element)

def element_present(driver,id):
    element = WebDriverWait(driver, 30).until(
              EC.presence_of_element_located((By.XPATH, id))
              )
    return 

HOME = os.getenv("HOME")

# setup logging
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/daily_tennis_data/status.log")  # change to DEBUG to see log all updates

def get_latest_odds():
    global live_market_ids
    global latest_odds
    global get_odds_error

    get_odds_error = False
    print(f"{datetime.now().strftime('%H:%M:%S')} : Started live odds")
    logging.info(f"{datetime.now().strftime('%H:%M:%S')} : Started live odds")
    

    latest_odds_info_dict = {}
    HOME = os.getenv("HOME")
    with open(f"{HOME}/pass_info.json","r") as f:
        pass_info = json.load(f)
    # create trading instance
    trading = betfairlightweight.APIClient(pass_info["betfair"]["username"], pass_info["betfair"]["password"] , app_key=pass_info["betfair"]["app_key"],certs=f'{HOME}/login_tokens/betfair')

    # login
    caught_trap = False
    try:
        trading.login()
        # Grab all event type ids. This will return a list which we will iterate over to print out the id and the name of the sport
        ## Market filter for event type does not work well
        #tennis_market_filter = betfairlightweight.filters.market_filter(text_query="Tennis")
        #event_types = trading.betting.list_event_types(filter=tennis_market_filter)
        event_types = trading.betting.list_event_types()
    except:
        caught_trap = True

    if not caught_trap:
        for event in event_types:
            if event.event_type.name == "Tennis":
                tennis_id = event.event_type.id

    if not caught_trap:
        try:
            tennis_event_filter = betfairlightweight.filters.market_filter(event_type_ids=[tennis_id],in_play_only=True)
            onging_tennis_events = trading.betting.list_events(filter=tennis_event_filter)
        except:
            caught_trap = True

    if not caught_trap:
        market_id_list = []
        for tennis_event in onging_tennis_events:
            p1 = re.sub(r"(.*?) v .*",r"\1",tennis_event.event.name)
            p2 = re.sub(r".*? v (.*)",r"\1",tennis_event.event.name)
            id = tennis_event.event.id
            market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=[id])
            try:
                market_catalogues = trading.betting.list_market_catalogue(
                                        filter=market_catalogue_filter,
                                        max_results='1000'
                                    )
            except:
                caught_trap = True
                break

            
            for market in market_catalogues:
                market_id = market.market_id
                market_name = market.market_name
                if market_name in ["Match Odds","Set 1 Winner","Set 2 Winner","Set 3 Winner","Set 4 Winner","Set 5 Winner"]:
                    market_id_list.append(market_id)
                    latest_odds_info_dict.update({market_id:{"players" : [p1,p2],
                                                            "market_name" : market_name}})

    if not caught_trap:
        market_id_list += live_market_ids
    
        while len(market_id_list) > 0:
            if len(market_id_list) > 25:
                current_market_id_list = market_id_list[0:25]
                del market_id_list[0:25]
            else:
                current_market_id_list = market_id_list
                market_id_list = []

            price_filter = betfairlightweight.filters.price_projection(
                                    price_data=['EX_BEST_OFFERS']
                                )
            try:
                market_book = trading.betting.list_market_book(market_ids=current_market_id_list,
                                                            price_projection=price_filter)
            except:
                caught_trap = True
                break

            for market in market_book:
                status = market.status
                market_id = market.market_id
                not_valid_market_id = (market_id not in latest_odds_info_dict.keys()) and \
                                    (market_id not in live_market_ids)
                if not_valid_market_id :
                    continue
                if market_id not in latest_odds_info_dict.keys():
                    latest_odds_info_dict.update({market_id:{"players"     : latest_odds[market_id]["players"].copy(),
                                                            "market_name" : latest_odds[market_id]["market_name"]}})

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
                latest_odds_info_dict[market_id].update({"status"  : status,
                                                        "runners" : runner_list})
        

    try:
        trading.logout()
    except:
        pass

    if not caught_trap:
        latest_odds = latest_odds_info_dict.copy()
    else:
        get_odds_error = True
    print(f"{datetime.now().strftime('%H:%M:%S')} : Completed live odds")
    logging.info(f"{datetime.now().strftime('%H:%M:%S')} : Completed live odds")

def get_live_scores():
    global game_set_info
    global get_set_error
    get_set_error = False
    print(f"{datetime.now().strftime('%H:%M:%S')} : Started live scores")
    logging.info(f"{datetime.now().strftime('%H:%M:%S')} : Started live scores")


    game_set_info_snapshot = game_set_info.copy()
    for game in game_set_info.keys():
        game_set_info[game]["sample"] = False
    
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

    try:
        driver.get("https://www.betfair.com/exchange/plus/inplay/tennis")
        element_clickable(driver,'.//ours-button/a[text()="Tennis"]')

        games_loaded = False
        while True:
            if selenium.__version__ == "3.14.0":
                game_list = driver.find_elements_by_xpath(".//a[@class='mod-link']")
            else:
                game_list = driver.find_elements(By.XPATH,".//a[@class='mod-link']")
            for game in game_list:
                if selenium.__version__ == "3.14.0":
                    try:
                        set_home = game.find_element_by_xpath(".//span[@class='home']")
                        games_loaded = True
                    except:
                        continue
                else:
                    try:
                        set_home = game.find_element(By.XPATH,".//span[@class='home']")
                        games_loaded = True
                    except:
                        continue

            if len(game_list) == 0 or not games_loaded:
                time.sleep(1) 
            else:
                break      

        count = 0
        game_keys = []
        while True:
            print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} searching game {count}")
            logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} searching game {count}")
            found_new_game = False
            if selenium.__version__ == "3.14.0":
                game_list = driver.find_elements_by_xpath(".//a[@class='mod-link']")
            else:
                game_list = driver.find_elements(By.XPATH,".//a[@class='mod-link']")

            for game in game_list:
                view_element(driver,game)
                if selenium.__version__ == "3.14.0":
                    try:
                        set_home = int(game.find_element_by_xpath(".//span[@class='home']").text)
                    except:
                        continue
                    set_away = int(game.find_element_by_xpath(".//span[@class='away']").text)
                    try:
                        current_score_home = int(game.find_element_by_xpath(".//div[@class='home']").text)
                        current_score_away = int(game.find_element_by_xpath(".//div[@class='away']").text)
                    except:
                        current_score_home = 0
                        current_score_away = 0
                    runner_list = game.find_elements_by_xpath(".//ul[@class='runners']/li")
                    home_runner = runner_list[0].text
                    away_runner = runner_list[1].text
                else:
                    try:
                        set_home = int(game.find_element(By.XPATH,".//span[@class='home']").text)
                    except:
                        continue
                    set_away = int(game.find_element(By.XPATH,".//span[@class='away']").text)
                    try:
                        current_score_home = int(game.find_element(By.XPATH,".//div[@class='home']").text)
                        current_score_away = int(game.find_element(By.XPATH,".//div[@class='away']").text)
                    except:
                        current_score_home = 0
                        current_score_away = 0
                    runner_list = game.find_elements(By.XPATH,".//ul[@class='runners']/li")
                    home_runner = runner_list[0].text
                    away_runner = runner_list[1].text

                game_set_key = f"{home_runner} v {away_runner}"
                if game_set_key not in game_keys:
                    found_new_game = True
                    game_keys.append(game_set_key)

                if game_set_key in game_set_info.keys():
                    current_score = [[set_home,current_score_home],[set_away,current_score_away]]
                    if current_score != game_set_info[game_set_key]["current_score"]:
                        game_set_info[game_set_key]["current_score"] = current_score
                        game_set_info[game_set_key]["sample"] = True
                else:
                    game_set_info.update({game_set_key : {"current_score" : [[set_home,current_score_home],[set_away,current_score_away]],
                                                        "sample"        : True}})

            if not found_new_game:
                break
            
            if count >= 100:
                break
            count += 1
    except Exception as e:
        pprint(e)
        get_set_error = True
        game_set_info = game_set_info_snapshot


    try:
        driver.quit()
    except:
        pass


    print(f"{datetime.now().strftime('%H:%M:%S')} : Completed live scores")
    logging.info(f"{datetime.now().strftime('%H:%M:%S')} : Completed live scores")

def get_current_set_odd_sample():
    global game_set_info
    global live_market_ids
    global latest_odds

    HOME = os.getenv("HOME")
    lock = FileLock(f"{HOME}/serialise")
    lock.acquire()

    print(f"Lock acquired at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
    logging.info(f"Lock acquired at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")

    t=threading.Thread(target=get_live_scores)
    t.start()

    t1 = threading.Thread(target=get_latest_odds)
    t1.start()
    t.join()
    lock.release()
    print(f"Lock released at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
    logging.info(f"Lock released at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
    t1.join()


def prepare_daily_data():
    global live_market_ids
    global game_set_info
    global latest_odds
    global daily_tennis_data
    found_update = False
    for market_id,market in latest_odds.items():
        market_name = market["market_name"]
        try:
            status = market["status"]
        except:
            continue

        players = market["players"]
        player_key = f"{players[0]} v {players[1]}"
        player_key1 = f"{players[1]} v {players[0]}"
        odds = [market["runners"][0]["odds"],market["runners"][1]["odds"]]
        odds1 = [market["runners"][1]["odds"],market["runners"][0]["odds"]]

        if status == "CLOSED":
            try:
                live_market_ids.remove(market_id)
                print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} : removing {market_id} from the live list")
                logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} : removing {market_id} from the live list")
            except:
                print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} could not find {market_id} in live_market_ids")
                logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} could not find {market_id} in live_market_ids")
            if market["runners"][0]["status"] == "WINNER":
                final_stat = [1,0]
                final_stat1 = [0,1]
            else:
                final_stat = [0,1]
                final_stat1 = [1,0]
            
        else:
            
            final_stat = [0,0]
            final_stat1 = [0,0]
        

        key_in_data = player_key in daily_tennis_data.keys()
        key1_in_data = player_key1 in daily_tennis_data.keys()

        key_in_game_set = player_key in game_set_info.keys()
        key1_in_game_set = player_key1 in game_set_info.keys()

        update_needed = (key_in_game_set and game_set_info[player_key]["sample"]) or \
                        (key1_in_game_set and game_set_info[player_key1]["sample"]) or \
                        ((key_in_data or key1_in_data) and status == "CLOSED")

        if update_needed:

            if not found_update:
                print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} update found on {player_key}")
                logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} update found on {player_key}")
            found_update = True

        if key_in_game_set:
            current_score = game_set_info[player_key]["current_score"]
            current_score1 = [game_set_info[player_key]["current_score"][1],game_set_info[player_key]["current_score"][0]]
        elif key1_in_game_set:
            current_score = game_set_info[player_key1]["current_score"]
            current_score1 = [game_set_info[player_key1]["current_score"][1],game_set_info[player_key1]["current_score"][0]]
        else:
            current_score = []
            current_score1 = []


        if update_needed:
            if not(key1_in_data or key_in_data):
                if status != "CLOSED":
                    daily_tennis_data.update({player_key : {market_id : {"market_name"    : market_name,
                                                                        "score_odd_list" : [{"current_score" : current_score.copy(),"odds" : odds.copy()}]}}})
                    daily_tennis_data[player_key][market_id].update({"final_stat" : final_stat.copy()})
                    live_market_ids.append(market_id)
            elif key_in_data:
                if status != "CLOSED":
                    if market_id in daily_tennis_data[player_key].keys():
                        daily_tennis_data[player_key][market_id]["score_odd_list"].append({"current_score" : current_score.copy(),"odds" : odds.copy()})
                    else:
                        daily_tennis_data[player_key].update({market_id : {"market_name"    : market_name,
                                                                            "score_odd_list" : [{"current_score" :current_score.copy(),"odds" : odds.copy()}]}})
                        live_market_ids.append(market_id)
                if final_stat[0] != 0 or final_stat[1] != 0 :
                    print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} : closing {market_id} in daily tennis data")
                    logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} : closing {market_id} in daily tennis data")
                daily_tennis_data[player_key][market_id]["final_stat"] = final_stat.copy()
            elif key1_in_data:
                if status != "CLOSED":
                    if market_id in daily_tennis_data[player_key1].keys():
                        daily_tennis_data[player_key1][market_id]["score_odd_list"].append({"current_score" : current_score1.copy(),"odds" : odds1.copy()})
                    else:
                        daily_tennis_data[player_key1].update({market_id : {"market_name"    : market_name,
                                                                            "score_odd_list" : [{"current_score" : current_score1.copy(),"odds" : odds1.copy()}]}})
                        live_market_ids.append(market_id)
                if final_stat[0] != 0 or final_stat[1] != 0 :
                    print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} : closing {market_id} in daily tennis data")
                    logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} : closing {market_id} in daily tennis data")
                daily_tennis_data[player_key1][market_id]["final_stat"] = final_stat1.copy()


    for market_id in live_market_ids:
        market_id_found = False
        for game in daily_tennis_data.keys():
            if market_id in daily_tennis_data[game].keys():
                if daily_tennis_data[game][market_id]["final_stat"] == [0,0]:
                    market_id_found = True
        if not market_id_found:
            print(f"{market_id} is in live but not the daily data")
            logging.info(f"{market_id} is in live but not the daily data")

    for game in daily_tennis_data.keys():
        for market_id in daily_tennis_data[game].keys():
            if daily_tennis_data[game][market_id]["final_stat"] == [0,0]:
                if market_id not in live_market_ids:
                    print(f"{market_id} is in daily_tennis_data but not in live")
                    logging.info(f"{market_id} is in daily_tennis_data but not in live")

    if found_update:
        print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} found something to update")        
        logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} found something to update")        

def store_data(file):
    global daily_tennis_data
    global live_market_ids
    HOME = os.getenv("HOME")
    todays_data = {}
    removal_list = []
    print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} Preparing data for the previous day")
    logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} Preparing data for the previous day")
    for game in daily_tennis_data.keys():
        all_markets_complete = True
        for market_id in daily_tennis_data[game].keys():
            stat_non_zero = (daily_tennis_data[game][market_id]["final_stat"][0] !=0 ) or \
                            (daily_tennis_data[game][market_id]["final_stat"][1] !=0)
            if market_id not in live_market_ids:
                if not stat_non_zero:
                    logging.info(f"{market_id} not in live but did not complete")
                    with open("temp.json","w") as f :
                        json.dump(daily_tennis_data,f)
                        exit()
            else:
                if stat_non_zero:
                    logging.info(f"{market_id} in live but completed")
                    with open("temp.json","w") as f :
                        json.dump(daily_tennis_data,f)
                all_markets_complete = False
        if all_markets_complete:
            print(f"Storing {game} into today's data")
            todays_data.update({game : daily_tennis_data[game].copy()})
            removal_list.append(game)
    for game in removal_list:
        daily_tennis_data.pop(game)
    with open(file,"w") as f:
        json.dump(todays_data,f) 


game_set_info = {}
live_market_ids = []
latest_odds = {}
daily_tennis_data = {}
get_set_error = False
get_odds_error = False

current_day = datetime.now()

count = 0
while True:
    daily_tennis_data_current = daily_tennis_data.copy()
    live_market_ids_current = live_market_ids.copy()
    latest_odds_before = latest_odds.copy()
    game_set_info_before = game_set_info.copy()
    get_current_set_odd_sample()

    if not(get_set_error or get_odds_error):
        prepare_daily_data()
    else:
        print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} Got error set : {get_set_error} odds : {get_odds_error}")

    # Check that there should be only additions to market ids
    error = False
    market_ids_before = []
    market_ids_after = []
    for game in daily_tennis_data.keys():
        for market_id in daily_tennis_data[game].keys():
            market_ids_after.append(market_id)
    for game in daily_tennis_data_current.keys():
        for market_id in daily_tennis_data_current[game].keys():
            market_ids_before.append(market_id)
    
    for market_id in market_ids_before:
        if market_id not in market_ids_after:
            print(f"{market_id} was in before but not after")
            logging.info(f"{market_id} was in before but not after")
            error = True
            break

    # Check that all market ids are in live
    for game in daily_tennis_data.keys():
        for market_id in daily_tennis_data[game].keys():
            if daily_tennis_data[game][market_id]["final_stat"] == [0,0]:
                if market_id not in live_market_ids:
                    pprint(f"{market_id} in daily but not live")
                    logging.info(f"{market_id} in daily but not live")
                    error = True
                    break
        if error:
            break
    
    ## Check that finished games cannot re start
    for game in daily_tennis_data.keys():
        for market_id in daily_tennis_data[game].keys():
            if market_id in market_ids_before:
                final_stat_before = daily_tennis_data_current[game][market_id]["final_stat"]
                final_stat_after = daily_tennis_data[game][market_id]["final_stat"]
                if final_stat_before != [0,0] and final_stat_after == [0,0]:
                    print(f"{market_id} was started again")
                    logging.info(f"{market_id} was started again")
                    error = True
                    break
        if error :
            break

    if error:        
        with open("daily_tennis_data_before.json","w") as f:
            json.dump(daily_tennis_data_current,f)
        with open("daily_tennis_data_after.json","w") as f:
            json.dump(daily_tennis_data,f)
        with open("live_market_ids_before.json","w") as f :
            live_dict = {"market_ids":live_market_ids_current}
            json.dump(live_dict,f) 
        with open("live_market_ids_after.json","w") as f :
            live_dict = {"market_ids":live_market_ids}
            json.dump(live_dict,f) 
        with open("game_set_info_before.json","w") as f :
            json.dump(game_set_info_before,f)
        with open("game_set_info_after.json","w") as f :
            json.dump(game_set_info,f)  
        with open("latest_odds_before.json","w") as f :
            json.dump(latest_odds_before,f) 
        with open("latest_odds_after.json","w") as f :
            json.dump(latest_odds,f) 
        exit()        
        
    get_set_error = False
    get_odds_error = False
    with open(f"{HOME}/script_stat/daily_tennis_data/shutdown","r") as f:
        file_lines = f.readlines()

    if int(file_lines[0]) == 1:
        print(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} shutdown of the script")
        logging.info(f"{datetime.now().strftime('%d:%m:%Y:%H:%M')} shutdown of the script")
        with open(f"{HOME}/database/tennis/live_data/{current_day.strftime('%d_%m_%Y')}_data.json","w") as f:
            json.dump(daily_tennis_data,f)
            break

    if current_day.day != datetime.now().day:
        store_data(f"{HOME}/database/tennis/live_data/{current_day.strftime('%d_%m_%Y')}_data.json")
        current_day = datetime.now()
        if os.path.exists(f"{HOME}/script_stat/daily_tennis_data/status_prev.log"):
            os.remove(f"{HOME}/script_stat/daily_tennis_data/status_prev.log")
        shutil.move(f"{HOME}/script_stat/daily_tennis_data/status.log",f"{HOME}/script_stat/basic_betting/status_prev.log")
        file_handler = logging.FileHandler(f"{HOME}/script_stat/daily_tennis_data/status.log")
        log = logging.getLogger()
        for hndler in log.handlers:
            if isinstance(hndler,logging.FileHandler):
                log.removeHandler(hndler)
        log.addHandler(file_handler)
    time.sleep(10)
    # count +=1 
    # if count >= 1:
    #     break




