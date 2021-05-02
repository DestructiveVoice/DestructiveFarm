from server.models import FlagStatus, SubmitResult
import random

def submit_flags(flags, config):

    for item in flags:
        status = random.choice([FlagStatus.ACCEPTED, FlagStatus.REJECTED])
        yield SubmitResult(item.flag, status, str(status))
