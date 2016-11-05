#!/usr/bin/env python3

import sys
from checker import Checker
import checker
from networking import State
import random
import json

async def handler_check(hostname):
	unregistered = State(hostname)
	listener = unregistered.get_listener()
	state = State(hostname)
	username, password = await state.register()
	wanted, contents = await state.put_posts(username, 5)
	await unregistered.get_contents(contents)
	listener.want_many(wanted)
	await listener.finish()
	checker.ok()

async def handler_get(hostname, id, flag):
	id = json.loads(id)
	user = id['username']
	state = State(hostname)
	await state.get_post(id['public'], True, user)
	file = await state.get_post(id['private'], True, user)
	if file['body'] != flag:
		return checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, file['body']))
	checker.ok()

async def handler_put(hostname, id, flag):
	state = State(hostname)
	public_before = random.randrange(2) == 0
	username, password = await state.register()
	await state.put_posts(username, random.randrange(3), True)
	if public_before:
		public_id, _, _, _ = await state.put_post(public=True, signed=True, username=username)
	else:
		private_id, _, _, _ = await state.put_post(body=flag, public=False, signed=True, username=username)
	await state.put_posts(username, random.randrange(3), True)
	if not public_before:
		public_id, _, _, _ = await state.put_post(public=True, signed=True, username=username)
	else:
		private_id, _, _, _ = await state.put_post(body=flag, public=False, signed=True, username=username)
	await state.put_posts(username, random.randrange(3), True)
	checker.ok(message="{}".format(json.dumps({'username': username, 'private': private_id, 'public': public_id})))

def main():
	checker = Checker(handler_check, [(handler_put, handler_get)])
	checker.process(sys.argv)

if __name__ == "__main__":
	main()
