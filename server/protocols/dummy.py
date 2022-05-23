from pprint import pprint
import string
from server.models import FlagStatus, SubmitResult
import random


def submit_flags(flags, config):

    for item in flags:
        status = random.choice([FlagStatus.ACCEPTED, FlagStatus.REJECTED])
        yield SubmitResult(item.flag, status, str(status))


def get_attack_info(config):
    # Generate random string
    def get_random_string(length):
        return "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
        )

    return {get_random_string(10): get_random_string(10) for _ in range(50000)}

def get_attack_info_service(config):
    return {"teams": [{"name": "Team1", "ip": ""}, {"name": "Team2", "ip": ""}]}


def get_teams(config):
    return {"Team1": "io"}
