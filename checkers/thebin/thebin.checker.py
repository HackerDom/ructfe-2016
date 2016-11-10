#!/usr/bin/env python3

import sys
from checker import Checker
import checker
from networking import State
import random
import json

def get_pair_of_strings():
	return checker.get_rand_string(5) + ' ' + checker.get_rand_string(5)

async def handler_check(hostname):

	unregistered = State(hostname)
	listener = unregistered.get_listener()
	state = State(hostname)
	username, password = await state.login()
	wanted, contents = await state.put_posts(username, 5)
	await unregistered.get_contents(contents)
	listener.want_many(wanted)

	skills = [get_pair_of_strings() for i in range(random.randint(3, 5))]
	skill = random.choice(skills)
	viewer = State(hostname)
	user, _ = await viewer.login(skills=json.dumps(skills))
	writer = State(hostname)
	username, _ = await writer.login()
	url, public, title, body, _ = await writer.put_post(public=True, need_skill=True, skill=skill)
	listener.want(url, username)
	await viewer.get_content(url, title, body)

	await listener.finish()
	checker.ok()

async def handler_get_1(hostname, id, flag):
	id = json.loads(id)
	user = id['username']
	state = State(hostname)
	await state.get_post(id['public'], True, user)
	file = await state.get_post(id['private'], True, user)
	if file['body'] != flag:
		return checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, file['body']))
	checker.ok()

async def handler_put_1(hostname, id, flag):
	state = State(hostname)
	public_before = random.randrange(2) == 0
	username, password = await state.login()
	await state.put_posts(username, random.randrange(3), True)
	if public_before:
		public_id, _, _, _, _ = await state.put_post(public=True, signed=True, username=username)
	else:
		private_id, _, _, _, _ = await state.put_post(body=flag, public=False, signed=True, username=username)
	await state.put_posts(username, random.randrange(3), True)
	if not public_before:
		public_id, _, _, _, _ = await state.put_post(public=True, signed=True, username=username)
	else:
		private_id, _, _, _, _ = await state.put_post(body=flag, public=False, signed=True, username=username)
	await state.put_posts(username, random.randrange(3), True)
	checker.ok(message=json.dumps({'username': username, 'private': private_id, 'public': public_id}))

async def handler_get_2(hostname, id, flag):
	id = json.loads(id)
	state = State(hostname)
	skill = id["skill"]
	await state.login(skills=json.dumps([skill]))
	url = id["url"]
	file = await state.get_post(url, True, 	id['username'])
	if file['body'] != flag:
		return checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, file['body']))
	checker.ok()

async def handler_put_2(hostname, id, flag):
	state = State(hostname)
	username, _ = await state.login()
	url, _, _, _, skill = await state.put_post(body=flag, public=True, signed=True, username=username, need_skill=True)
	checker.ok(message=json.dumps({'username': username, 'url': url, 'skill': skill}))

def main():
	checker = Checker(handler_check, [(handler_put_1, handler_get_1), (handler_put_2, handler_get_2)])
	checker.process(sys.argv)

if __name__ == "__main__":
	main()
