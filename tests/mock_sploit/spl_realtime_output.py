#!/usr/bin/env python3
"""
It's better to process output of this sploit in real-time.
This is a test sploit for such a functionality in the farm client.
For clarity, use --not-per-team mode in the client.
"""

import hashlib
import os
import time


def main():
    for i in range(10):
        flag = hashlib.sha256(os.urandom(10)).hexdigest()[:31] + '='
        print(flag)
        # sys.stdout.flush()
        # Thanks to PYTHONUNBUFFERED=1, this sploit should work even without calling flush.

        time.sleep(5)


if __name__ == '__main__':
    main()
