CONFIG = {
    # Don't forget to remove the old database (flags.sqlite) before each competition.

    # The clients will run sploits on TEAMS and
    # fetch FLAG_FORMAT from sploits' stdout.

    # WARNING: THIS IS A FALLBACK DICTIONARY IF THE PROTOCOL DOES NOT PROVIDE UPDATED TEAMS.
    'TEAMS': {'Team #{}'.format(i): '10.0.0.{}'.format(i) for i in range(1, 29 + 1)},

        
    'FLAG_FORMAT': r'[a-zA-Z0-9]{31}=',

    # This configures how and where to submit flags.
    # The protocol must be a module in protocols/ directory.

    'SYSTEM_PROTOCOL': 'dummy',
    # 'ATTACK_INFO_ENDPOINT': "http://#FIXME",
    # 'SYSTEM_HOST': '127.0.0.1',
    # 'SYSTEM_PORT': 31337,
    # 'TEAM_TOKEN': 'your_secret_token',

    # The server will submit not more than SUBMIT_FLAG_LIMIT flags
    # every SUBMIT_PERIOD seconds. Flags received more than
    # FLAG_LIFETIME seconds ago will be skipped.

    'SUBMIT_FLAG_LIMIT': 250,
    'SUBMIT_PERIOD': 60,
    'FLAG_LIFETIME': 11 * 60,

    # Password for the web interface. You can use it with any login.
    # This value will be excluded from the config before sending it to farm clients.
    'SERVER_PASSWORD': '1234',

    # Use authorization for API requests
    'ENABLE_API_AUTH': False,
    'API_TOKEN': '00000000000000000000'
}
