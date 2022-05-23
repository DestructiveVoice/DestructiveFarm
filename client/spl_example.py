#!/usr/bin/env python3

import json
import random
import string
import sys

print(
    "Hello! I am a little sploit. I could be written on any language, but "
    "my author loves Python. Look at my source - it is really simple. "
    "I should steal flags and print them on stdout or stderr. "
)

# The host to attack is passed as the first argument.
host = sys.argv[1]

# The path of the attack info json is passed as the second argument.
with open(sys.argv[2]) as f:
    attack_info = json.loads(f.read())

print(f"I need to attack a team with host: {host}")
print(f"I recieved this attack info: {attack_info}")

print("Here are some random flags for you:")


def spam_flag():
    arr = [random.choice(string.ascii_uppercase + string.digits) for _ in range(31)]
    flag = "".join(arr) + "="
    print(flag, flush=True)

spam_flag()
