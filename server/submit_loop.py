import importlib
import random
import time
from collections import defaultdict

from server import app, database, reloader
from server.models import FlagStatus, SubmitResult


def get_fair_share(groups, limit):
    groups = sorted(groups, key=len)
    places_left = limit
    group_count = len(groups)
    fair_share = places_left // group_count

    result = []
    residuals = []
    for group in groups:
        if len(group) <= fair_share:
            result += group

            places_left -= len(group)
            group_count -= 1
            fair_share = places_left // group_count
            # The fair share could have increased because the processed group
            # had a few elements. Sorting order guarantees that the smaller
            # groups will be processed first.
        else:
            selected = random.sample(group, fair_share + 1)
            result += selected[:-1]
            residuals.append(selected[-1])

    return result + random.sample(residuals, limit - len(result))


def submit_flags(flags, config):
    module = importlib.import_module('server.protocols.' + config['SYSTEM_TYPE'])

    app.logger.debug('Submitting %s flags', len(flags))
    try:
        return module.submit_flags(flags, config)
    except Exception as e:
        message = '{}: {}'.format(type(e), str(e))
        app.logger.error('Exception on submitting flags: %s', message)
        return [SubmitResult(item.flag, FlagStatus.QUEUED, message) for item in flags]


def run_loop():
    with app.app_context():
        db = database.get()

    while True:
        config = reloader.get_config()
        submit_start_time = time.time()

        skip_time = round(submit_start_time - config['FLAG_LIFETIME'])
        db.execute("UPDATE flags SET status = '?' WHERE status = ? AND time < ?",
                   FlagStatus.SKIPPED.name, FlagStatus.QUEUED.name, skip_time)
        db.commit()

        flags = db.execute("SELECT * FROM flags WHERE status = ?", FlagStatus.QUEUED.name).fetchall()

        if flags:
            grouped_flags = defaultdict(list)
            for item in flags:
                grouped_flags[item.sploit, item.team].append(item)
            flags = get_fair_share(grouped_flags, config['SUBMIT_FLAG_LIMIT'])

            results = submit_flags(flags, config)

            rows = [(item.status.name, item.checksystem_response, item.flag) for item in results]
            db.executemany("UPDATE flags SET status = ?, checksystem_response = ? "
                           "WHERE flag = ?", rows)
            db.commit()

        submit_spent = time.time() - submit_start_time
        if config['SUBMIT_PERIOD'] > submit_spent:
            time.sleep(config['SUBMIT_PERIOD'] - submit_spent)
