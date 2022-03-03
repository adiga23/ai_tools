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
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/basic_betting/status.log")  # change to DEBUG to see log all updates


def get_latest_odds():
    global latest_odds
    latest_odds = {}
    print(f"{datetime.now().strftime('%H:%M:%S')} : Started live odds")

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
                    latest_odds.update({market_id:{"players"      : [p1,p2],
                                                    "market_name" : market_name}})

    if not caught_trap:
    
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

                ## We are only tracking live market ids in this function
                if status == "CLOSED":
                    latest_odds.pop(market_id)
                    continue

                not_valid_market_id = (market_id not in latest_odds.keys())

                if not_valid_market_id :
                    continue

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
                latest_odds[market_id].update({"status"  : status,
                                               "runners" : runner_list})
                
        

    try:
        trading.logout()
    except:
        pass

    if caught_trap:
        latest_odds = {}

    print(f"{datetime.now().strftime('%H:%M:%S')} : Completed live odds")

def get_live_scores():
    global game_set_info
    game_set_info = {}
    print(f"{datetime.now().strftime('%H:%M:%S')} : Started live scores")


    
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

            current_score = [[set_home,current_score_home],[set_away,current_score_away]]
            if game_set_key in game_set_info.keys():
                if current_score != game_set_info[game_set_key]:
                    print(f"{game_set_key} : current_score is not equal to the one which exists")
            else:
                game_set_info.update({game_set_key : current_score})

        if not found_new_game:
            break
        
        if count >= 100:
            break
        count += 1

    try:
        driver.quit()
    except:
        pass

    print(f"{datetime.now().strftime('%H:%M:%S')} : Completed live scores")

def track_market_ids():
    global market_id_tracker
    global market_id_tracker_status

    print(f"{datetime.now().strftime('%H:%M:%S')} : Started market_id_tracker")

    HOME = os.getenv("HOME")
    with open(f"{HOME}/pass_info.json","r") as f:
        pass_info = json.load(f)
    # create trading instance
    trading = betfairlightweight.APIClient(pass_info["betfair"]["username"], pass_info["betfair"]["password"] , app_key=pass_info["betfair"]["app_key"],certs=f'{HOME}/login_tokens/betfair')

    # login
    caught_trap = False
    try:
        trading.login()
    except:
        caught_trap = True

    if not caught_trap:
        market_id_list = list(market_id_tracker.keys())
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
                if status != "CLOSED":
                    continue
                else:
                    print(f"{market_id} was closed")
                not_valid_market_id = (market_id not in current_market_id_list)

                if not_valid_market_id :
                    continue

                market_id_status = {}
                for runner in market.runners:
                    selection_id = runner.selection_id
                    runner_status = runner.status
                    if runner_status == "WINNER":
                        market_id_status.update({selection_id:True})
                    else:
                        market_id_status.update({selection_id:False})
                if market_id in market_id_tracker_status.keys():
                    print(f"{market_id} found in market_id_tracker_status")
                else:
                    market_id_tracker_status.update({market_id:market_id_status})
                

    try:
        trading.logout()
    except:
        pass

    if caught_trap:
        market_id_tracker_status = {}

    print(f"{datetime.now().strftime('%H:%M:%S')} : Completed market_id_traker")


def get_current_set_odd_sample():
    HOME = os.getenv("HOME")
    lock = FileLock(f"{HOME}/serialise")
    lock.acquire()
    print(f"Lock acquired at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
    logging.info(f"Lock acquired at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
    t=threading.Thread(target=get_live_scores)
    t.start()

    t1 = threading.Thread(target=get_latest_odds)
    t1.start()

    t2 = threading.Thread(target=track_market_ids)
    t2.start()

    t.join()

    lock.release()
    print(f"Lock released at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")
    logging.info(f"Lock released at {datetime.now().strftime('%d/%m/%Y:%H:%M')}")

    t1.join()
    t2.join()


#def place_track():
    



def track_bets():
    global market_id_tracker
    global market_id_tracker_status
    global avail_cash
    global total_lost_cash
    global full_cash
    global total_won_cash

    for market_id in market_id_tracker_status.keys():
        ## if the odds have not been completed wait
        if market_id not in market_id_tracker.keys():
            continue
        selection_id = market_id_tracker[market_id]["selection_id"]

        if selection_id not in market_id_tracker_status[market_id].keys():
            pprint(f"selection id {selection_id} not found in market_id {market_id}")
            logging.info(f"selection id {selection_id} not found in market_id {market_id}")
               
        if market_id_tracker_status[market_id][selection_id]:
            cash_generated = market_id_tracker[market_id]["bet_price"] * market_id_tracker[market_id]["cash_to_bet"] * 0.95
            pprint(f"market_id {market_id} won the bet and generated cash {cash_generated}")
            logging.info(f"market_id {market_id} won the bet and generated cash {cash_generated}")
            market_id_tracker.pop(market_id)
            ## Add the cash generated to the available cash
            avail_cash += cash_generated
            ## Add profit to full cash
            full_cash += (cash_generated - market_id_tracker[market_id]["cash_to_bet"])
            total_won_cash += (cash_generated - market_id_tracker[market_id]["cash_to_bet"])
        else:
            cash_lost = market_id_tracker[market_id]["cash_to_bet"]
            pprint(f"market_id {market_id} lost the bet and generated cash {cash_lost}")
            logging.info(f"market_id {market_id} won the bet and generated cash {cash_lost}")
            market_id_tracker.pop(market_id)
            full_cash -= cash_lost
            total_lost_cash += cash_lost



def place_bet():
    global game_set_info
    global latest_odds
    global market_id_tracker
    global full_cash 
    global avail_cash

    odd_diff = 4
    per_bet_perc = 0.1
    min_odd = 1.1

    ## Only bet 10%  of full cash
    max_cash_per_bet = per_bet_perc * full_cash
        
    ## If there is not available cash continue
    if max_cash_per_bet > avail_cash:
        return


    for market_id in latest_odds:
        ## Already placed the bet previously
        if market_id in market_id_tracker.keys():
            continue

        ## There is no odds to bet on
        if latest_odds[market_id]["runners"] == []:
            continue

        empty_odds = False
        for runner in latest_odds[market_id]["runners"]:
            if runner["odds"] == []:
                empty_odds = True

        ## Even if one of the odds is empty then continue 
        if empty_odds:
            continue

        selection_id0 = latest_odds[market_id]["runners"][0]["selection_id"]
        selection_id1 = latest_odds[market_id]["runners"][1]["selection_id"]
        odds0 = latest_odds[market_id]["runners"][0]["odds"].copy()
        odds1 = latest_odds[market_id]["runners"][1]["odds"].copy()

        found_odd0 = False
        found_odd1 = False
        bet_price0 = 0
        bet_price1 = 0

        max_return = 0
        cash_to_bet = 0

        for i in range(0,len(odds0)):
            for j in range(0,len(odds1)):
                if odds1[j]["price"] - odds0[i]["price"] >= odd_diff:
                    if odds0[i]["price"] >= min_odd:
                        found_odd0 = True
            if found_odd0:
                if odds0[i]["size"] > max_cash_per_bet:
                    current_return = max_cash_per_bet * odds0[i]["price"]
                    current_cash = max_cash_per_bet
                else:
                    current_return = odds0[i]["size"] * odds0[i]["price"]
                    current_cash = odds0[i]["size"]

                if current_return > max_return:
                    bet_price0 = odds0[i]["price"]
                    max_return = current_return
                    cash_to_bet = current_cash

        max_return = 0
        
        for i in range(0,len(odds1)):
            for j in range(0,len(odds0)):
                if odds0[j]["price"] - odds1[i]["price"] >= odd_diff:
                    if odds1[i]["price"] >= min_odd:
                        found_odd1 = True

            if found_odd1:
                if odds1[i]["size"] > max_cash_per_bet:
                    current_return = max_cash_per_bet * odds1[i]["price"]
                    current_cash = max_cash_per_bet
                else:
                    current_return = odds1[i]["size"] * odds1[i]["price"]
                    current_cash = odds1[i]["size"]

                if current_return > max_return:
                    bet_price1 = odds1[i]["price"]
                    max_return = current_return
                    cash_to_bet = current_cash

        ## Have we found a favourable odd
        if found_odd0:
            selection_id = selection_id0
            bet_price = bet_price0
            player = 0
        elif found_odd1:
            selection_id = selection_id1
            bet_price = bet_price1
            player = 1
        else:
            continue

        market_name = latest_odds[market_id]["market_name"]
        players = latest_odds[market_id]["players"]
        player_key1  = f"{players[0]} v {players[1]}"
        player_key2 = f"{players[1]} v {players[0]}"

        key1_in_set = player_key1 in game_set_info.keys()
        key2_in_set = player_key2 in game_set_info.keys()

        key_in_set = key1_in_set or key2_in_set

        if key1_in_set:
            player_key = player_key1
        else:
            player_key = player_key2

        # If the players info is not in game set info then continue
        if not key_in_set:
            continue        
 
        set_info = (game_set_info[player_key][0][0],game_set_info[player_key][1][0])
        game_info = (game_set_info[player_key][0][1],game_set_info[player_key][1][1])

        if market_name == "Match Odds":
            if player == 0:
                if set_info[0] > set_info[1]:
                    pprint(f"placing bet on maket_id : {market_id} id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    logging.info(f"placing bet on id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    market_id_tracker.update({market_id : {"selection_id" : selection_id,
                                                           "bet_price"    : bet_price,
                                                           "cash_to_bet"  : cash_to_bet}})
                    avail_cash -= cash_to_bet
                    
                else:
                    continue
            else:
                if set_info[1] > set_info[0]:
                    pprint(f"placing bet on market_id : {market_id} id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    logging.info(f"placing bet on id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    market_id_tracker.update({market_id : {"selection_id" : selection_id,
                                                           "bet_price"    : bet_price,
                                                           "cash_to_bet"  : cash_to_bet}})
                    avail_cash -= cash_to_bet
                else:
                    continue
        else:
            if player == 0:
                if game_info[0] - game_info[1] >= 2:
                    pprint(f"placing bet on id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    logging.info(f"placing bet on market_id : {market_id} id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    market_id_tracker.update({market_id : {"selection_id" : selection_id,
                                                           "bet_price"    : bet_price,
                                                           "cash_to_bet"  : cash_to_bet}})
                    avail_cash -= cash_to_bet
                else:
                    continue
            else:
                if game_info[1] - game_info[0] >= 2:
                    pprint(f"placing bet on id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    logging.info(f"placing bet on market_id : {market_id} id : {selection_id} price {bet_price} cash to bet {cash_to_bet}")
                    market_id_tracker.update({market_id : {"selection_id" : selection_id,
                                                           "bet_price"    : bet_price,
                                                           "cash_to_bet"  : cash_to_bet}})
                    avail_cash -= cash_to_bet
                else:
                    continue          

game_set_info = {}
latest_odds = {}
market_id_tracker = {}
market_id_tracker_status = {}
full_cash = 100
avail_cash = 100
total_lost_cash = 0
total_won_cash = 0

current_date = datetime.now()
while True:
    pprint(f"full cash {full_cash} avail_cash {avail_cash} lost_cash {total_lost_cash} won_cash {total_won_cash}")
    get_current_set_odd_sample()
    place_bet()
    track_bets()
    if datetime.now().day != current_date.day:
        if os.path.exists(f"{HOME}/script_stat/basic_betting/status_prev.log"):
            os.remove(f"{HOME}/script_stat/basic_betting/status_prev.log")
        shutil.move(f"{HOME}/script_stat/basic_betting/status.log",f"{HOME}/script_stat/basic_betting/status_prev.log")
        file_handler = logging.FileHandler(f"{HOME}/script_stat/basic_betting/status.log")
        log = logging.getLogger()
        for hndler in log.handlers:
            if isinstance(hndler,logging.FileHandler):
                log.removeHandler(hndler)
        log.addHandler(file_handler)
    time.sleep(10)


    


