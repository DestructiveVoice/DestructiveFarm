from themis.finals.attack.helper import Helper
from themis.finals.attack.result import Result

from server.models import FlagStatus, SubmitResult


RESPONSES = {
    FlagStatus.ACCEPTED: [Result.SUCCESS_FLAG_ACCEPTED],
    FlagStatus.REJECTED: [Result.ERROR_FLAG_EXPIRED, Result.ERROR_FLAG_YOURS,
                          Result.ERROR_FLAG_SUBMITTED, Result.ERROR_FLAG_NOT_FOUND],
}


def submit_flags(flags, config):
    h = Helper(config['SYSTEM_HOST'])
    codes = h.attack(*[item.flag for item in flags])

    for item, code in zip(flags, codes):
        for status, possible_codes in RESPONSES.items():
            if code in possible_codes:
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED

        yield SubmitResult(item.flag, found_status, code.name)
