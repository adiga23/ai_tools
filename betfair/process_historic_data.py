import os
import bz2
from datetime import datetime
from datetime import timedelta
import json
import time
import logging
from pprint import pprint

HOME = os.getenv("HOME")
logging.basicConfig(level=logging.INFO,filemode="w",filename=f"{HOME}/script_stat/process_historic_data/status.log")  # change to DEBUG to see log all updates


curr_date = datetime(2015,4,1)
# curr_date = datetime(2019,2,8)
day = timedelta(days=1)
end_date = datetime(2022,2,5)
# end_date = datetime(2019,2,8)


id_info_dict = {}
odds_id_mapping = {}
game_odds_list = []
event_filter_dict = {}

games_info_dir = f"{HOME}/database/tennis/games_info"

while curr_date <= end_date:
    next_date = curr_date + day
    while not os.path.exists(f"{HOME}/database/tennis/{next_date.strftime('%d_%m_%Y')}"):
        print(f"Waiting for {next_date.strftime('%d_%m_%Y')}")
        logging.info(f"Waiting for {next_date.strftime('%d_%m_%Y')}")
        time.sleep(300)
    database_dir = f"{HOME}/database/tennis/{curr_date.strftime('%d_%m_%Y')}"
    os.chdir(database_dir)
    print(f"processing {curr_date.strftime('%d_%m_%Y')}")
    logging.info(f"processing {curr_date.strftime('%d_%m_%Y')}")

    num_files = len(os.listdir(database_dir))

    
    for i in range(0,num_files):
        f = bz2.BZ2File(f"{database_dir}/file_{i}.bz2","r")
        # if curr_date == datetime(2015,6,6):
        #     print(f"Reading file {database_dir}/file_{i}.bz2")
        try:
            file_lines = f.readlines()
        except:
            continue
        for line in file_lines:
            try:
                line_dict = json.loads(line)
            except:
                continue
            if "mc" not in line_dict.keys():
                continue
            for data in line_dict["mc"]:
                if "rc" in data.keys():
                    odds_list = data["rc"]
                    for odd in odds_list:
                        id = odd['id']
                        odd_value = odd["ltp"]
                        if id not in odds_id_mapping.keys():
                            continue
                        event_id = odds_id_mapping[id]
                        if id_info_dict[event_id][id] == 0:
                            id_info_dict[event_id]["p0_odds"].append(odd_value)
                        else:
                            id_info_dict[event_id]["p1_odds"].append(odd_value)

                if "marketDefinition" in data.keys():
                    if "marketType" not in data["marketDefinition"].keys():
                        continue
                    if (data["marketDefinition"]["marketType"] != "MATCH_ODDS"):
                        continue
                    if ("bettingType" not in data["marketDefinition"].keys() ):
                        continue
                    if ("status" not in data["marketDefinition"].keys()) :
                        continue
                    if ("runners" not in data["marketDefinition"].keys()) :
                        continue
                    if (len(data["marketDefinition"]["runners"]) != 2):
                        continue
                    id = data["marketDefinition"]["eventId"]
                    odds_id = data["id"]
                    
                    date = datetime.strptime(data["marketDefinition"]["marketTime"],"%Y-%m-%dT%H:%M:%S.%fz")
                    is_match_odds = (data["marketDefinition"]["bettingType"] == "ODDS") and \
                                    (data["marketDefinition"]["marketType"] == "MATCH_ODDS")
                    
                    is_new_match_odds = is_match_odds and \
                                        (data["marketDefinition"]["status"] == "OPEN")

                    is_close_match_odds = is_match_odds and \
                                          (data["marketDefinition"]["status"] == "CLOSED")

                    p0_dict = data["marketDefinition"]["runners"][0]
                    p1_dict = data["marketDefinition"]["runners"][1]
                    both_players_active = (p0_dict["status"] == "ACTIVE") and \
                                          (p1_dict["status"] == "ACTIVE")

                    if is_new_match_odds and both_players_active and (id not in id_info_dict.keys()):
                        new_id_dict = {id : {p0_dict["name"] : 0,
                                             p0_dict["id"]   : 0,
                                             p1_dict["name"] : 1,
                                             p1_dict["id"]   : 1,
                                             "p0_odds"       : [],
                                             "p1_odds"       : [],
                                             "date"          : date.strftime("%d/%m/%Y")}}

                        
                        odds_id_mapping.update({p0_dict["id"] : id,
                                                p1_dict["id"] : id})
                        id_info_dict.update(new_id_dict)


                    if is_close_match_odds :
                        p0_exists = p0_dict["id"] in odds_id_mapping.keys()
                        p1_exists = p1_dict["id"] in odds_id_mapping.keys()

                        if not(p0_exists and p1_exists) and (p0_exists or p1_exists):
                            if p0_exists:
                                event_id = odds_id_mapping[p0_dict["id"]]
                            if p1_exists:
                                event_id = odds_id_mapping[p1_dict["id"]]

                            remove_list = []
                            for key in odds_id_mapping.keys():
                                if odds_id_mapping[key] == event_id:
                                    remove_list.append(key)
                            for id in remove_list:
                                odds_id_mapping.pop(id)
                            id_info_dict.pop(event_id)
                        elif (p0_exists or p1_exists):
                            event_id = odds_id_mapping[p0_dict["id"]]
                            odds_id_mapping.pop(p0_dict["id"])
                            odds_id_mapping.pop(p1_dict["id"])
                            game_dict = id_info_dict[event_id].copy()
                            date = game_dict["date"]
                            winner_found = (p0_dict["status"] == "WINNER") or \
                                           (p1_dict["status"] == "WINNER")
                            if p0_dict["status"] == "WINNER":
                                winner = game_dict[p0_dict["id"]]
                            else:
                                winner = game_dict[p1_dict["id"]]
                            game_dict.update({"winner" : winner})

                            game_dict.pop(p0_dict["id"])
                            game_dict.pop(p1_dict["id"])
                            
                            p0_odds_list = game_dict["p0_odds"]
                            p1_odds_list = game_dict["p1_odds"]
                            merge_odds = []
                            small_len_odds = len(p0_odds_list) if (len(p0_odds_list) < len(p1_odds_list)) else len(p1_odds_list)
                            for i in range(0,small_len_odds):
                                odds_pair = [p0_odds_list[i],p1_odds_list[i]]
                                merge_odds.append(odds_pair.copy())
                            game_dict.pop("p0_odds")
                            game_dict.pop("p1_odds")
                            game_dict.update({"odds" : merge_odds})
                            id_info_dict.pop(id)
                            if winner_found:
                                if date in event_filter_dict.keys():
                                    if event_id in event_filter_dict[date]:
                                        filtered = True
                                    else:
                                        filtered = False
                                else:
                                    filtered = False
                                if not filtered:
                                    game_odds_list.append(game_dict)
                                    if date in event_filter_dict.keys():
                                        event_filter_dict[date].append(event_id)
                                    else:
                                        event_filter_dict.update({date : [event_id]})

    prev_date = curr_date    
    curr_date += day
    json_dump = (curr_date > end_date) or \
                (curr_date.month != prev_date.month)
    if json_dump:
        json_dict = {"games_list" : game_odds_list}
        print(f"writing {prev_date.month}_{prev_date.year}.json with {len(game_odds_list)} entries")
        logging.info(f"writing {prev_date.month}_{prev_date.year}.json")
        
        with open(f"{games_info_dir}/{prev_date.month}_{prev_date.year}.json","w") as f:
            json.dump(json_dict,f)
        game_odds_list = []

