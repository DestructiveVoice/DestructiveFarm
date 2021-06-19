from server import app
from server.models import FlagStatus, SubmitResult
import requests
import json

RESPONSES = {
    FlagStatus.ACCEPTED: [
        "accepted",
    ],
    FlagStatus.REJECTED: [
        "old",
    ],
    FlagStatus.SKIPPED:
    ["Game is not available.", "already stolen", "own", "NOP"]
}


def submit_flags(flags, config):

    flags_to_send = [item.flag for item in flags]
    # app.logger.warning(flags_to_send)
    resps = requests.put(f"http://{config['SYSTEM_HOST']}/flags",
                         headers={"X-Team-Token": "fe56ef438aa1377c"},
                         json=flags_to_send)
    #app.logger.warning(resps.text)
    resps = resps.json()
    for result in resps:
        app.logger.warning(result)
        for status, substrings in RESPONSES.items():
            if any(s in result["msg"] for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED
            app.logger.warning(
                'Unknown checksystem response (flag will be resent): %s',
                result)

        yield SubmitResult(result["flag"], found_status, result["msg"])
