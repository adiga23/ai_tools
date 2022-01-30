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
import re
from fractions import Fraction
import sys
import json
import os
import multiprocessing

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

def element_exists(element, id):
    try:
        element.find_element_by_xpath(id)
    except:
        return False
    return True

def get_team_results(team1,team2):
    firefox_option = Options()
    # firefox_option.add_argument("--headless")
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")

    driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                               service_log_path=os.devnull)

    driver.get("https://www.google.com")
    driver.maximize_window()

    element_click(driver, "//div[text()='I agree']")

    element_click_send_key(driver,"//input[@title='Search']",f"{team1} vs {team2}")

    search_key = driver.find_elements_by_xpath("//input[@value='Google Search']")

    for key in search_key:
        if key.is_displayed() and key.is_enabled():
            try:
                key.click()
                break
            except:
                continue


    return
    # driver.quit()

def get_bet365_data(data_info):
    for key in data_info.keys():
        data_info[key]["entry_found"] = False
    firefox_option = Options()
    firefox_option.add_argument("--headless")
    firefox_option.add_argument("--window-size=1920,1080")
    firefox_option.add_argument("--incognito")

    driver = webdriver.Firefox(executable_path=firefox_path,options=firefox_option,
                               service_log_path=os.devnull)

    driver.get("https://www.bet365.com")
    driver.maximize_window()

    counter=5

    # Try clicking the element multiple times before giving up
    while counter > 0:
      try:
        element_click(driver,"//div[@class='hm-MainHeaderCentreWide_Link hm-HeaderMenuItem ']/div[text()='In-Play']")
        counter = 0
      except:
        if counter == 1 :
            driver.quit()
            return(False)
        else:
            counter = counter - 1
            time.sleep(2)

    counter=5
    while counter > 0:
      try:
        element_click(driver,"//div[text()='Tennis']")
        counter = 0
      except:
        if counter == 1 :
            driver.quit()
            return(False)
        else:
            counter = counter - 1
            time.sleep(2)


    time.sleep(5)

    # Getting competition Header
    try:
        data_list = driver.find_elements_by_xpath("//div[@class='ovm-Competition ovm-Competition-open ']")
    except:
        driver.quit()

    for data in data_list:
        driver.execute_script("arguments[0].scrollIntoView();", data)

        try:
            competition=data.find_element_by_xpath(".//div[@class='ovm-CompetitionHeader_Name ']").text
            subcompetitions = data.find_elements_by_xpath(".//div[@class='ovm-Fixture_Container']")
        except:
            continue

        for subcompetition in subcompetitions:
            try:
              # Get the information about the players
              teams=subcompetition.find_elements_by_xpath(".//div[@class='ovm-FixtureDetailsWithIndicators_Team ']")
              team_list = []
              for team in teams:
                  team_list.append(team.text)

              # Find the set the current game is going on
              if (element_exists(subcompetition,".//div[@class='ovm-FixtureDetailsWithIndicators_SetGameLabel ']")):
                  set_element=subcompetition.find_element_by_xpath(".//div[@class='ovm-FixtureDetailsWithIndicators_SetGameLabel ']")
                  set_text = re.sub(r'Set (.*?) .*', r'\1', set_element.text)
                  set = int(set_text)
                  game_text = re.sub(r'.*? Game (.*?)', r'\1', set_element.text)
                  game = int(game_text)
              else:
                  game = 0
                  set = 0

              # Get the team scores
              if element_exists(subcompetition, ".//div[@class='ovm-SetsBasedScoresTennis_TeamOne']"):
                  team1_score_list = subcompetition.find_elements_by_xpath(".//div[@class='ovm-SetsBasedScoresTennis_TeamOne']")
                  team1_score = []
                  for score in team1_score_list:
                      team1_score.append(score.text)
              else:
                  for i in range(0, 3):
                      team1_score.append("0")

              if element_exists(subcompetition, ".//div[@class='ovm-SetsBasedScoresTennis_TeamTwo']"):
                  team2_score_list = subcompetition.find_elements_by_xpath(".//div[@class='ovm-SetsBasedScoresTennis_TeamTwo']")
                  team2_score = []
                  for score in team2_score_list:
                      team2_score.append(score.text)

              # Get the odds for the team
              team_odds = []
              if element_exists(subcompetition, ".//div[@class='ovm-HorizontalMarket_Participant ovm-ParticipantOddsOnly gl-Participant_General ']"):
                  team_odds_list = subcompetition.find_elements_by_xpath(".//div[@class='ovm-HorizontalMarket_Participant ovm-ParticipantOddsOnly gl-Participant_General ']")
                  for odds in team_odds_list:
                      team_odds.append(float(Fraction(odds.text)))
              else:
                  team_odds = [0,0]

              if ((len(team_list) == 2)):
                  game_key = f"{competition}_{game}"
                  data_dict = {"name"        : competition,
                               "team1"       : team_list[0],
                               "team2"       : team_list[1],
                               "team1_score" : [int(team1_score[0]),int(team1_score[1])],
                               "team2_score" : [int(team2_score[0]),int(team2_score[1])],
                               "team1_odds"  : team_odds[0],
                               "team2_odds"  : team_odds[1],
                               "set"         : set,
                               "game"        : game,
                               "bet_placed"  : False,
                               "bet_team"    : 1,
                               "entry_found" : True}

                  if game_key not in data_info.keys():
                    data_info.update({game_key:data_dict})
                  else:
                    data_info[game_key]["team1_score"] = [int(team1_score[0]),int(team1_score[1])]
                    data_info[game_key]["team2_score"] = [int(team2_score[0]),int(team2_score[1])]
                    data_info[game_key]["team1_odds"]  = team_odds[0]
                    data_info[game_key]["team2_odds"]  = team_odds[1]
                    data_info[game_key]["set"]         = set
                    data_info[game_key]["entry_found"] = True
            except:
              continue

    driver.quit()

    return True

def run_job(cmdline):
  os.system(f'{cmdline}')

def keep_mac_alive():
    os.system("caffeinate &")
    #pid=multiprocessing.Process(target=run_job,args=("caffeinate",))
    #pid.start()
    return

# Opening JSON file
try:
    f = open('result.json','r')
    teams_data = json.load(f)
    f.close()
except:
    teams_data = {}

# keep_mac_alive()

# status=get_bet365_data(teams_data)
#
# with open('result.json', 'w') as fp:
#     json.dump(teams_data, fp)
#
# for key in teams_data.keys():
#     if teams_data[key]["entry_found"]:
#         print(f"{teams_data[key]['team1']} : {teams_data[key]['team1_odds']} {teams_data[key]['team2']} : {teams_data[key]['team2_odds']}")
#     else:
#         print(f"{teams_data[key]['team1']} vs {teams_data[key]['team2']} Finished")

get_team_results("Pauline Dore", "Sowjanya Bavisetti")
