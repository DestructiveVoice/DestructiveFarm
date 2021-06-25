#!/usr/bin/env python3

from time import sleep
import requests
import threading

DF_HOST = ""
SPLOIT_NAME = ""
resp = requests.get(f"http://{DF_HOST}:5000/api/get_config")
assert resp.status_code == 200
config = resp.json()


def send_flags(team_name, flags):
    sending = [{"flag": flag, "sploit": SPLOIT_NAME, "team": team_name}
               for flag in flags]
    requests.post(f"http://{DF_HOST}:5000/api/post_flags",
                  headers={"Content-type": "application/json"}, json=sending)


def get_flag_ids(flag_ids):

    return {}


def loop(team_name, ip, flag_id):
    flags = []

    ############# WRITE SCRIPT HERE #############
    
    #################### END ####################

    send_flags(team_name, flags)


while True:

    flag_ids = get_flag_ids(config["TEAMS"].copy())

    for team_name, ip in config["TEAMS"].items():
        if team_name not in flag_ids:
            flag_ids[team_name] = None
        threading.Thread(target=loop, args=(
            team_name, ip, flag_ids[team_name])).start()
    sleep(config["SUBMIT_PERIOD"])
