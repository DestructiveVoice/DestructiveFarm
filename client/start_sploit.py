#!/usr/bin/env python3

import argparse
import itertools
import json
import os
import re
import stat
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from urllib.parse import urljoin
from urllib.request import Request, urlopen


if sys.version_info < (3, 4):
    print('[-] Support of Python < 3.4 is not implemented yet')
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Run a sploit on all teams in a loop')

    parser.add_argument('sploit', help='Sploit executable')
    parser.add_argument('--server-url', default='http://farm.kolambda.com:5000', help='Server URL')

    parser.add_argument('--pool-size', type=int, default=50,
                        help='Maximal number of concurrent sploit instances'
                             '(too little will make time limits for sploits smaller,'
                             'too big will eat all RAM on your computer)')
    parser.add_argument('--attack-period', type=float, default=120,
                        help='Rerun the sploit on all teams each N seconds'
                             '(too little will make time limits for sploits smaller,'
                             'too big will miss flags from some rounds)')

    return parser.parse_args()


SCRIPT_EXTENSIONS = ['.pl', '.py', '.rb']


class InvalidSploitError(Exception):
    pass


def check_sploit(path):
    if not os.path.isfile(path):
        raise ValueError('No such file: {}'.format(path))

    is_script = os.path.splitext(path)[1].lower() in SCRIPT_EXTENSIONS
    if is_script:
        with open(path, 'rb') as f:
            if f.read(2) != b'#!':
                raise InvalidSploitError(
                    'Please use shebang (e.g. "#!/usr/bin/env python3") as a first line of your script')

    if os.name != 'nt':
        file_mode = os.stat(path).st_mode
        if not file_mode & stat.S_IXUSR:
            if is_script:
                print('[*] Setting the executable bit')
                os.chmod(path, file_mode | stat.S_IXUSR)
            else:
                raise InvalidSploitError("The provided file doesn't appear to be executable")


class APIException(Exception):
    pass


def get_config(args):
    with urlopen(urljoin(args.server_url, '/api/get_config')) as conn:
        if conn.status != 200:
            raise APIException(conn.read())

        return json.load(conn)


def post_flags(args, flags):
    sploit_name = os.path.basename(args.sploit)
    data = [{'flag': item['flag'], 'sploit': sploit_name, 'team': item['team']}
            for item in flags]

    req = Request(urljoin(args.server_url, '/api/post_flags'))
    req.add_header('Content-Type', 'application/json')
    with urlopen(req, data=json.dumps(data).encode()) as conn:
        if conn.status != 200:
            raise APIException(conn.read())


POST_PERIOD = 5
POST_FLAG_LIMIT = 10000


def validate_args(args, config):
    min_attack_period = config['FLAG_LIFETIME'] - config['SUBMIT_PERIOD'] - POST_PERIOD
    if args.attack_period >= min_attack_period:
        print("[~] Warning: --attack-period should be < {:.2f} sec, "
              "otherwise the sploit will not have time "
              "to catch flags for each round before their expiration".format(min_attack_period))


def once_in_a_period(period):
    for iter_no in itertools.count():
        start_time = time.time()
        yield iter_no

        time_spent = time.time() - start_time
        if period > time_spent:
            time.sleep(period - time_spent)


flags_seen = set()
flag_queue = []
flags_lock = threading.RLock()


def run_post_loop(args):
    global flag_queue

    for _ in once_in_a_period(POST_PERIOD):
        with flags_lock:
            flags_to_post = flag_queue[:POST_FLAG_LIMIT]

        if flags_to_post:
            try:
                post_flags(args, flags_to_post)

                with flags_lock:
                    flag_queue = flag_queue[len(flags_to_post):]

                print('[+] {} flags posted to the server ({} in the queue)'.format(
                    len(flags_to_post), len(flag_queue)))
            except Exception as e:
                print("[~] Can't post flags to the server: {}".format(repr(e)))
                print("[*] The flags will be posted next time")


def run_sploit(args, team_name, team_addr, iter_no, max_runtime, flag_format):
    need_close_fds = (os.name != 'nt')
    proc = subprocess.Popen([args.sploit, team_addr],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            bufsize=1, close_fds=need_close_fds)
    try:
        outs, _ = proc.communicate(timeout=max_runtime)
    except subprocess.TimeoutExpired:
        print('[~] Killing sploit for team "{}": {}'.format(team_name, team_addr))
        proc.kill()
        outs, _ = proc.communicate()
    # TODO: Get outputs in the real-time

    flags = flag_format.findall(outs)

    with flags_lock:
        for item in flags:
            if item not in flags_seen:
                flags_seen.add(item)
                flag_queue.append({'flag': item, 'team': team_name})


def main(args):
    try:
        check_sploit(args.sploit)
    except InvalidSploitError as e:
        print('[-] {}'.format(e))
        return

    print('[*] Connecting to the farm server at {}'.format(args.server_url))

    threading.Thread(target=lambda: run_post_loop(args), daemon=True).start()
    # FIXME: Don't use daemon=True, exit from the thread properly

    config = None
    for iter_no in once_in_a_period(args.attack_period):
        print('[*] Launching an attack (iteration {})'.format(iter_no))

        try:
            config = get_config(args)
        except Exception as e:
            print("[{}] Can't get config from the server: {}".format('-' if iter_no == 0 else '~', repr(e)))
            if iter_no == 0:
                return
            print('[*] Using the old config')

        if iter_no == 0:
            validate_args(args, config)
        max_runtime = args.attack_period / ceil(args.pool_size / len(config['TEAMS']))
        print("[*] Time limit for a sploit instance: {:.2f} sec "
              "(if this isn't enough, increase --pool-size or --attack-period)".format(max_runtime))

        flag_format = re.compile(config['FLAG_FORMAT'].encode())

        pool = ThreadPoolExecutor(max_workers=args.pool_size)
        for team_name, team_addr in config['TEAMS'].items():
            pool.submit(run_sploit, args, team_name, team_addr, iter_no, max_runtime, flag_format)
        pool.shutdown(wait=False)


if __name__ == '__main__':
    try:
        main(parse_args())
    except KeyboardInterrupt:
        pass
