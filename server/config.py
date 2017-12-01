CONFIG = {
    # The clients will run sploits on TEAMS and
    # fetch FLAG_FORMAT from sploits' stdout.
    'TEAMS': {
        'Bushwhackers': '10.0.0.1',
        'Corrupted Reflection': '10.0.0.2',
    },
    'FLAG_FORMAT': r'\w{31}=',

    # This configures how and where to submit flags.
    # The protocol must be a module in protocols/ directory.
    # RuCTF(E) and VolgaCTF checksystems are supported out-of-the-box.
    'SYSTEM_PROTOCOL': 'ructf',
    'SYSTEM_HOST': 'f.ructf.org',
    'SYSTEM_PORT': 31337,
    'SYSTEM_TIMEOUT': 5,

    # The server will submit not more than SUBMIT_FLAG_LIMIT flags
    # every SUBMIT_PERIOD seconds. Flags received more than
    # FLAG_LIFETIME seconds ago will be skipped.
    'SUBMIT_FLAG_LIMIT': 50,
    'SUBMIT_PERIOD': 5,
    'FLAG_LIFETIME': 5 * 60,
}
