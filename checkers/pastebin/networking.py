#!/usr/bin/env python3

import checker
import aiohttp
import random
import json
import queue
import asyncio

PORT = 8080

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
#	return cookies.OutputString()
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
						checher.corrupt(error='can\'t parse service responce', exception=ex)
					await self.queue.put((data['url'], data['owner']))
				elif msg.type == aiohttp.WSMsgType.CLOSED:
					break
				else:
					checker.corrupt(error='get message with unexpected type {}\nmessage: {}'.format(msg.type, msg.text))
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
	def __init__(self, hostname, port=8080):
		self.hostname = hostname
		self.port = '' if port is None else ':' + str(port)
		self.session = aiohttp.ClientSession()
		self.ua = 'browser'
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
	async def post(self, url, data):
		url = self.get_url(url)
		try:
			async with self.session.post(url, data=data) as response:
				await check_status(response)
				check_cookie(self.session.cookie_jar)
				return await response.text()
		except Exception as ex:
			checker.down(error='{}\n{}'.format(url, data), exception=ex)
	async def login(self, username, password):
		await self.post('login', {'user': username, 'password': password})
	async def logout(self):
		await self.get('logout')
	async def register(self, username=None, password=None):
		if username is None:
			username = checker.get_rand_string(8)
		if password is None:
			password = checker.get_rand_string(16)
		await self.post('register', {'user': username, 'password': password})
		return username, password
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
	async def put_post(self, title=None, body=None, public=None):
		if title is None:
			title = checker.get_rand_string(64)
		if body is None:
			body = checker.get_rand_string(1024)
		if public is None:
			public = random.randrange(2) == 0
		request = {'title': title, 'body': body}
		if public:
			request['is_public'] = 'on'
		url = json.loads(await self.post('publish', request))[0]
		return url, public, title, body
	async def put_posts(self, username, count=1):
		wanted = set()	
		content = set()
		unwanted = set()
		for i in range(count):
			url, public, title, body = await self.put_post()
			if public:
				wanted.add((url, username))
			content.add((url, title, body))
		return wanted, content
	async def get_private(self, url):
		response = await self.get(url)
		return json.loads(response)
	def check_public(self, username, url):
		wanted = set()
		wanted.add((url, username))
		self.get_publics(wanted, set())
	async def get_content(self, url, title, body):
		response = await self.get_private(url)
		if response['title'] != title:
			checker.mumble(message="wrong post title '{}': expexted '{}', found '{}'".format(url, title, response['title']))
		if response['body'] != body:
			checker.mumble(message="wrong post body '{}': expexted '{}', found '{}'".format(url, body, response['body']))
	async def get_contents(self, contents):
		for url, title, body in contents:
			await self.get_content(url, title, body)

