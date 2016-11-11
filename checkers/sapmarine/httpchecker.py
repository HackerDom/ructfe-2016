#!/usr/bin/env python3

import sys
import socket
import json
import os.path
import traceback
import requests as r

EXITCODE_OK            = 101
EXITCODE_CORRUPT       = 102
EXITCODE_MUMBLE        = 103
EXITCODE_DOWN          = 104
EXITCODE_CHECKER_ERROR = 110

class CheckException(Exception):
	def __init__(self, code, value):
		self.code = code
		self.value = value
	def __str__(self):
		return repr(self.value)

class HttpWebException(Exception):
	def __init__(self, value, path):
		self.value = value
		self.path = path
	def __str__(self):
		return repr(self.value)

class HttpCheckerBase(object):
	def check(self, addr):
		pass

	def get(self, addr, flag_id, flag):
		pass

	def put(self, addr, flag_id, flag):
		pass

	def debug(self, msg):
		sys.stderr.write('%s\n' % msg)

	def run(self):
		if len(sys.argv) < 2:
			self.debug('Not enough arguments')
			exit(EXITCODE_CHECKER_ERROR)
		script_name = os.path.basename(os.sys.argv[0])
		command = sys.argv[1]

		try:
			if command == 'info':
				print('vulns: 1')
				exit(EXITCODE_OK)

			if len(sys.argv) < 3:
				self.debug('Not enough arguments')
				exit(EXITCODE_CHECKER_ERROR)

			addr = sys.argv[2]

			if command == 'check':
				exit(self.check(addr))

			if len(sys.argv) < 6:
				self.debug('Not enough arguments')
				exit(EXITCODE_CHECKER_ERROR)

			flag_id, flag, vuln = sys.argv[3:6]

			if command == 'get':
				exit(self.get(addr, flag_id, flag, int(vuln)))

			if command == 'put':
				exit(self.put(addr, flag_id, flag, int(vuln)))

			self.debug('Invalid command')
			exit(EXITCODE_CHECKER_ERROR)
		except CheckException as e:
			print(e.value)
			exit(e.code)
		except HttpWebException as e:
			print('http {} status {}'.format(e.path, e.value))
			exit(EXITCODE_DOWN if e.value >= 500 else EXITCODE_MUMBLE)
		except (r.exceptions.ConnectionError, r.exceptions.Timeout) as e:
			self.debug(e)
			print('connection problem')
			exit(EXITCODE_DOWN)
		except (r.exceptions.HTTPError, r.exceptions.TooManyRedirects) as e:
			self.debug(e)
			print('invalid http response')
			exit(EXITCODE_MUMBLE)
		except socket.error as e:
			self.debug(e)
			if isinstance(e, socket.timeout) or 'errno' in dir(e) and e.errno == 111:
				print('connection problem')
				exit(EXITCODE_DOWN)
			print('socket error')
			exit(EXITCODE_MUMBLE)
		except Exception as e:
			self.debug('Error during execution')
			traceback.print_exc(100, sys.stderr)
			self.debug(e)
			exit(EXITCODE_CHECKER_ERROR)
