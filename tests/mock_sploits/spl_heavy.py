#!/usr/bin/env python3

import hashlib
import random
import requests
import sys
import time


def main():
    if random.random() < 0.1:
        raise Exception('The team service is down')

    text = sys.argv[1]

    for url in ['http://google.com', 'http://facebook.com']:
        for _ in range(3):
            text += requests.get(url).text
            time.sleep(0.1)

    if random.random() < 0.1:
        raise Exception('Bad luck')

    print('Text length:', len(text))

    for _ in range(10):
        text = hashlib.sha256(text.encode()).hexdigest()[:31].upper() + '='
        print(text, flush=True)
        time.sleep(0.1)


if __name__ == '__main__':
    main()
