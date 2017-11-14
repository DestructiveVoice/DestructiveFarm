from collections import namedtuple
from enum import Enum


class FlagStatus(Enum):
    QUEUED = 0
    SKIPPED = 1
    ACCEPTED = 2
    REJECTED = 3


Flag = namedtuple('Flag', ['flag', 'sploit', 'team', 'time', 'status', 'checksystem_response'])
SubmitResult = namedtuple('SubmitResult', ['flag', 'status', 'checksystem_response'])
