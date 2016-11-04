#!/usr/bin/env python3

import sys
from checker import Checker
import checker
from networking import State
import asyncio
import random

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
	user, private = id.split()
	state = State(hostname)
	file = await state.get_private(private)
	if 'body' not in file:
		return checker.corrupt(message="Fail reciving post body")
	if file['body'] != flag:
		return checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, file['body']))
	checker.ok()

async def handler_put(hostname, id, flag):
	state = State(hostname)
	public_before = random.randrange(2) == 0
	username, password = await state.register()
	await state.put_posts(username, random.randrange(3))
	if public_before:
		public_id, _, _, _ = await state.put_post(public=True)
	else:
		private_id, _, _, _ = await state.put_post(body=flag, public=False)
	await state.put_posts(username, random.randrange(3))
	if not public_before:
		public_id, _, _, _ = await state.put_post(public=True)
	else:
		private_id, _, _, _ = await state.put_post(body=flag, public=False)
	await state.put_posts(username, random.randrange(3))
	checker.ok(message="{}\n{}".format(username, private_id))

async def main():
	checker = Checker(handler_check, [(handler_put, handler_get)])
	await checker.process(sys.argv)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
	loop.close()
