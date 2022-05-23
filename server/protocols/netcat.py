import socket
from time import time

import requests

from server import app
from server.models import Flag, FlagStatus, SubmitResult

RESPONSES = {
    FlagStatus.ACCEPTED: ["accepted", "congrat", "valid"],
    FlagStatus.REJECTED: ["invalid", "illegal", "old"],
    FlagStatus.SKIPPED: ["resubmit", "ownflag"],
}


def submit_flags(flags: list[Flag], config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.connect((config["SYSTEM_HOST"], config["SYSTEM_PORT"]))
        
        for item in flags:
            sock.send(item.flag.encode())
            response = sock.recv(4096).decode(errors="ignore").lower()

            for status, substrings in RESPONSES.items():
                if any(s in response for s in substrings):
                    found_status = status
                    break
            else:
                found_status = FlagStatus.QUEUED
                app.logger.warning(
                    "Unknown checksystem response (flag will be resent): %s", response
                )

            yield SubmitResult(item.flag, found_status, response)


def get_teams(config):
    attack_info = get_attack_info(config)
    if "teams" not in attack_info:
        return {}

    teams = attack_info["teams"]

    return {obj["name"]: obj["ip"] for obj in teams}


def get_attack_info(config):
    # Handle the case of not specified attack endpoint
    if "ATTACK_INFO_ENDPOINT" not in config:
        return {}

    global last_config_check
    global last_config
    curr_time = time.time()

    if (curr_time - last_config_check) > config["SUBMIT_PERIOD"]:
        resp = requests.get(config["ATTACK_INFO_ENDPOINT"])

        try:
            last_config = resp.json()
            last_config_check = curr_time
        except Exception as e:
            app.logger.warning("Error while downloading attack json: {}".format(e))

    return last_config
