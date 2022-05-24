from pprint import pprint
import string
from server.models import FlagStatus, SubmitResult
import random


def submit_flags(flags, config):

    for item in flags:
        status = random.choice([FlagStatus.ACCEPTED, FlagStatus.REJECTED])
        yield SubmitResult(item.flag, status, str(status))


# Generate random string
def _random_string(length: int) -> str:
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(length)
    )


def get_attack_info(config):
    return {_random_string(10): _random_string(10) for _ in range(100)}


def get_attack_info_service(config):
    return {"teams": [{"name": "Team1", "ip": ""}, {"name": "Team2", "ip": ""}]}


def get_teams(config):
    return {"Team1": "10.0.0.1", "Team2": "10.0.0.2", "Team3": "10.0.0.3"}
