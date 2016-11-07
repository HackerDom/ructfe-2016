#! /usr/bin/env python

import random, string

key = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
value = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(31)) + '='

print("\x01\x00\x00\x00" + key + value)