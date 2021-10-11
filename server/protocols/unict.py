from server import app
from server.models import FlagStatus, SubmitResult
import requests
import json

MATRICOLA = "AAAAAA" #EDIT ME
RESPONSES = {
    FlagStatus.ACCEPTED: [
        "accettata",
    ],
    FlagStatus.REJECTED: [
        "vecchia",
    ],
    FlagStatus.SKIPPED:[
      "Own", 
      "NOP",
      "Error"
    ]
}

def submit_flags(flags, config):

    flags_to_send = [item.flag for item in flags]
    resps = requests.put(f"http://{config['SYSTEM_HOST']}/unict/flagsrv",
                         headers={"X-Team-Token": "unict"},
                         json=flags_to_send)
    resps = resps.json()
    for result in resps:
        app.logger.warning(result)
        for status, substrings in RESPONSES.items():
            if any(s in result["msg"] for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED

        yield SubmitResult(result["flag"], found_status, result["msg"])
