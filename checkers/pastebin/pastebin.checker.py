#!/usr/bin/env python3

import sys
import traceback
import requests
import string
import random
import json
import queue

from ws4py.client.threadedclient import WebSocketClient

PORT = 8080

def ructf_error(status=110, message=None, error=None, exception=None):
	if message:
		sys.stdout.write(message)
		sys.stdout.write("\n")

	sys.stderr.write("{}\n".format(status))
	if error:
		sys.stderr.write(error)
		sys.stderr.write("\n")

	if exception:
		print(dir(exception))
		sys.stderr.write("Exception: {}\n".format(exception))
		traceback.print_tb(exception.__traceback__, file=sys.stderr)

	sys.exit(status)

def service_ok(status=101, message="Service OK", *args, **kwargs):
	return ructf_error(status, message, *args, **kwargs)

def service_corrupt(status=102, *args, **kwargs):
	return ructf_error(status, *args, **kwargs)

def service_mumble(status=103, *args, **kwargs):
	return ructf_error(status, *args, **kwargs)

def service_down(status=104, *args, **kwargs):
	return ructf_error(status, *args, **kwargs)

def make_err_message(message, request, reply):
	return "{}\n->\n{}\n<-\n{}\n=".format(message, request, reply)

def get_rand_string(l):
	return ''.join(random.choice(string.ascii_lowercase) for _ in range(l + random.randint(-l//2, l//2)))

def check_status(response):
	if response.status_code != 200:
		service_mumble(error='status code is {}. Content: {}\n'.format(response.status_code, response.text))
		
def check_cookie(cookies):
	if cookies is None:
		service_mumble(error='no cookies =(')
	if (not 'auth' in cookies) or (cookies.get('auth') == ''):
		service_mumble(error="auth cookie not found. '{}'".format(cookies))

def check_response(response):
	check_status(response)
	check_cookie(response)

def get_cookie_string(cookies):
	return '; '.join([str(key) + '=' + str(value) for key, value in cookies.items()])


class WSClient(WebSocketClient):
	def set_handler(self, handler, finisher):
		self.handle = handler
		self.finish = finisher
	def received_message(self, m):
		try:
			data = json.loads(str(m))
		except Exception as ex:
			service_corrupt(exception=ex)
		self.handle(data['url'], data['owner'])
	def closed(self, code, reasone):
		self.finish()

class WSHelper:
	def __init__(self, url, origin, ua, cookie):
		ws = WSClient(url, headers=[
			('Origin', origin),
			('User-Agent', ua),
			('Cookie', get_cookie_string(cookie))
		])
		self.queue = queue.Queue()
		self.wanted = set()
		self.closed = False
		try:
			ws.deamon = True
			ws.set_handler(self.add, self.close_connection)
			ws.connect()
		except Exception as ex:
			service_corrupt(exception=ex)

	def add(self, url, owner):
		self.queue.put((url, owner))
	def want(self, url, owner):
		self.wanted.add((url, owner))
	def close_connection(self):
		self.closed = True
	def finish(self):
		while len(self.wanted) > 0 and (not self.closed or not self.queue.empty()):
			try:
				top = self.queue.get(timeout=10)
			except queue.Empty as ex:
				if self.closed:
					break
				service_corrupt(error='too slow')
			if top in self.wanted:
				self.wanted.remove(top)
		if len(self.wanted) > 0:
			service_corrupt(error='fail getting all posted files')

class State:
	def __init__(self, hostname):
		base_addr = '://{}:{}/'.format(hostname, PORT)
		self.base_addr = 'http' + base_addr
		self.ws_addr = 'ws' + base_addr
		self.session = requests.Session()
		self.ua = 'browser'
	def get(self, url):
		url = self.base_addr + url
		response = None
		try:
			response = self.session.get(url)
		except Exception as ex:
			service_down(error=url, exception=ex)
		check_status(response)
		return response
	def post(self, url, d):
		url = self.base_addr + url
		response = None
		try:
			response = self.session.post(url, data=d)
		except Exception as ex:
			service_down(error='{}\n{}'.format(url, d), exception=ex)
		check_status(response)
		check_cookie(self.session.cookies)
		return response
	def post_file(self, url, is_public, filename, filedata):
		url = self.base_addr + url
		data = {'is_public' : 'on'} if is_public else None
		request = requests.Request('POST', url, files=[('file', [filename, filedata, 'text/plain'])], data=data)
		try:
			request = self.session.prepare_request(request)
			response = self.session.send(request)
		except Exception as ex:
			service_down(error='{}\n{}'.format(url, d), exception=ex)
		check_status(response)
		check_cookie(self.session.cookies)
		return json.loads(response.text)[0]
	def login(self, username, password):
		return self.post('login', {'user': username, 'password': password})
	def logout(self):
		return self.get('logout')
	def register(self):
		username = get_rand_string(8)
		password = get_rand_string(16)
		self.post('register', {'user': username, 'password': password})
		return username, password
	def get_private(self, url):
		return self.get(url)
	def get_public(self, username, url):
		helper = self.get_listener()
		helper.want((url, username))
		helper.finish()
	def get_publics(self, wanted):
		listener = self.get_listener()
		for url, owner in wanted:
			listener.want(url, owner)
		listener.finish()
	def get_listener(self):
		return WSHelper(self.ws_addr + 'publics', self.base_addr, self.ua,  self.session.cookies)
	def put_file(self, data=None):
		if data is None:
			data = get_rand_string(64)
		filename = get_rand_string(10)
		url = self.post_file('upload', True, filename, data)
		return url, True
	def put_files(self, username):
		listener = self.get_listener()
		wanted = set()	
		for i in range(1):
			url, public = self.put_file()
			if public:
				wanted.add((url, username))
				listener.want(url, username)
		print('post')
		listener.finish()
		print('get 1')
		return wanted

def handler_info(*args):
	service_ok(message="vulns: 1")

def handler_check(*args):
	hostname = args[0][0]
	state = State(hostname)
	username, password = state.register()
	print('register')
	wanted = state.put_files(username)
	state = State(hostname)
	state.get_publics(wanted)
	print('get 2')

def handler_get(args):
	hostname, id, flag, vuln = args
	user, private, public = id.split()
	state = State(hostname)
	file = state.get_private(private)
	state.check_public(user, public)
	if file != flag:
		return service_corrupt(message="Bad flag")
	return service_ok()

def handler_put(args):
# TODO
	return service_ok(message="{}\n{}\n{}\n{}".format(username, password, dashboard, name))

HANDLERS = {
	'info' : handler_info,
	'check' : handler_check,
	'get' : handler_get,
	'put' : handler_put,
}

def main():
	handler = HANDLERS[sys.argv[1]]
	handler(sys.argv[2:])


if __name__ == "__main__":
	main()
