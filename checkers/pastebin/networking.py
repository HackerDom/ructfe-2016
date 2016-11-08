#!/usr/bin/env python3

import checker
import aiohttp
import random
import queue
import asyncio
from crypto import Signer

import UserAgents

async def check_status(response):
	if response.status != 200:
		checker.mumble(error='status code is {}. Content: {}\n'.format(response.status, await response.text()))
		
def check_cookie(cookies):
	if cookies is None:
		checker.mumble(error='no cookies =(')
	for cookie in cookies:
		if cookie.key == 'auth':
			return
	checker.mumble(error="auth cookie not found. '{}'".format(get_cookie_string(cookies)))

async def check_response(response):
	await check_status(response)
	check_cookie(response)

def get_cookie_string(cookies):
	return '; '.join([str(cookie.key) + '=' + str(cookie.value) for cookie in cookies])

class WSHelper:
	def __init__(self, connection):
		self.connection = connection
		self.queue = asyncio.Queue()
		self.wanted = set()
	def start(self):
		asyncio.async(self.start_internal())
	async def start_internal(self):
		async with self.connection as ws:
			async for msg in ws:
				if msg.type == aiohttp.WSMsgType.TEXT:
					try:
						data = msg.json(loads = lambda s : checker.parse_json(s, ['url', 'owner']))
					except Exception as ex:
						checher.mumble(error='can\'t parse service responce', exception=ex)
					await self.queue.put((data['url'], data['owner']))
				elif msg.type == aiohttp.WSMsgType.CLOSED:
					break
				else:
					checker.mumble(error='get message with unexpected type {}\nmessage: {}'.format(msg.type, msg.text))
	def want(self, url, owner):
		self.wanted.add((url, owner))
	def want_many(self, wanted):
		self.wanted |= wanted
	async def finish(self):
		while len(self.wanted) > 0:
			top = await self.queue.get()
			if top in self.wanted:
				self.wanted.remove(top)
		self.connection.close()

class State:
	def __init__(self, hostname, port=80):
		self.hostname = hostname
		self.port = '' if port is None else ':' + str(port)
		self.session = aiohttp.ClientSession(headers={
			'Referer': self.get_url(''), 
			'User-Agent': UserAgents.get()
		})
		self.signer = Signer()
	def __del__(self):
		self.session.close()
	def get_url(self, path='', proto='http'):
		return '{}://{}{}/{}'.format(proto, self.hostname, self.port, path.lstrip('/'))
	async def get(self, url):
		url = self.get_url(url)
		try:
			async with self.session.get(url) as response:
				await check_status(response)
				return await response.text()
		except Exception as ex:
			checker.down(error=url, exception=ex)
	async def post(self, url, data={}, need_check_status=True):
		url = self.get_url(url)
		try:
			async with self.session.post(url, data=data) as response:
				if need_check_status:
					await check_status(response)
				check_cookie(self.session.cookie_jar)
				if need_check_status:
					return await response.text()
				else:
					return response.status, await response.text()
		except Exception as ex:
			checker.down(error='{}\n{}'.format(url, data), exception=ex)
	async def login(self, username, password):
		await self.register(username, password)
	async def logout(self):
		await self.post('logout')
	async def register(self, username=None, password=None):
		can_retry = username is None
		if username is None:
			username = checker.get_rand_string(8)
		if password is None:
			password = checker.get_rand_string(16)
		status, text = await self.post('register', {'user': username, 'password': password}, need_check_status = False)
		if status == 200:
			return username, password
		if status == 400 and can_retry:
			while status == 400:
				username = checker.get_rand_string(16)
				password = checker.get_rand_string(32)
				status, text = await self.post('register', {'user': username, 'password': password}, need_check_status = False)
			return username, password
		checker.mumble(error='error while register: status {}, response {}'.format(status, text))
	async def update_skill(self, skills):
		await self.post('set-skills', {'skills': skills})
	async def get_private(self, url):
		return await self.get(url)
	def get_listener(self):
		url = self.get_url('publics', proto='ws')
		try:
			connection = self.session.ws_connect(url, origin=self.get_url(''))
		except Exception as ex:
			checker.down(exception=ex)
		helper = WSHelper(connection)
		helper.start()
		return helper
	async def put_post(self, title=None, body=None, public=None, signed=False, username=None, need_skill=False):
		if title is None:
			title = checker.get_rand_string(16)
		if body is None:
			body = checker.get_rand_string(1024)
		if public is None:
			public = random.randrange(2) == 0
		request = {'title': title, 'body': body}
		if public:
			request['is_public'] = 'on'
		if signed:
			request['sign'] = self.signer.sign(self.hostname, username, request)
		if need_skill:
			request['requirement'] = checker.get_rand_string(10)
		response = await self.post('publish', request)
		url = checker.parse_json(response)[0]
		return url, public, title, body
	async def put_posts(self, username, count=1, signed=False):
		wanted = set()	
		content = set()
		for i in range(count):
			url, public, title, body = await self.put_post(username=username, signed=signed)
			if public:
				wanted.add((url, username))
			content.add((url, title, body))
		return wanted, content
	async def get_post(self, url, signed=False, username=None):
		response = await self.get(url)
		data = checker.parse_json(response, ['title', 'body'])
		if signed and not self.signer.check(self.hostname, username, data):
			checker.mumble(error='fail check sign for url {}'.format(url))
		return data
	def check_public(self, username, url):
		wanted = set()
		wanted.add((url, username))
		self.get_publics(wanted, set())
	async def get_content(self, url, title, body):
		response = await self.get_post(url)
		if response['title'] != title:
			checker.mumble(error="wrong post title '{}': expexted '{}', found '{}'".format(url, title, response['title']))
		if response['body'] != body:
			checker.mumble(error="wrong post body '{}': expexted '{}', found '{}'".format(url, body, response['body']))
	async def get_contents(self, contents):
		for url, title, body in contents:
			await self.get_content(url, title, body)