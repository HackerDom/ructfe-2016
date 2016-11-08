#!/usr/bin/env python3

from sys import argv, stderr
import subprocess
import requests
import socket
import random

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


def check(*args):
	addr, vuln, *use_internal_port = args

	data = str(random.random())[2:]
	signature = subprocess.check_output('./signtool ' + data, shell=True).strip().decode('ascii')

	port = 16780 if use_internal_port else 80
	url = 'http://%s:%s/%s' % (addr, port, data)
	try:
		r = requests.get(url)
		if r.status_code != 200:
			print("Failed to GET: got unexpected code " + str(r.status_code), file=stderr)
			exit(MUMBLE)
		if not "Signature: " + signature in r.text:
			print("Web page does not contain valid signature", file=stderr)
			exit(MUMBLE)
	except Exception as e:
		print("Failed to GET: " + str(e), file=stderr)
		exit(DOWN)

	exit(OK)

def put(*args):
	addr, flag_id, flag, vuln = args

	request = b'\x01\x00\x00\x00' + flag_id.replace('-', '').encode('ascii') + flag.encode('ascii')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		s.connect((addr, 16761))
	except:
		print("Failed to connect to control port", file=stderr)
		exit(DOWN)

	try:
		s.send(request)
	except Exception as e:
		print("Failed to communicate through control port: " + str(e), file=stderr)
		exit(DOWN)

	s.close()

	exit(OK)

def get(*args):
	addr, flag_id, flag, vuln = args

	request = b'\x00\x00\x00\x00' + flag_id.replace('-', '').encode('ascii')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		s.connect((addr, 16761))
	except:
		print("Failed to connect to control port", file=stderr)
		exit(DOWN)

	try:
		s.send(request)
		data = s.recv(4 + 12 + 32)
	except Exception as e:
		print("Failed to communicate through control port: " + str(e), file=stderr)
		exit(DOWN)

	s.close()

	received_flag = data.decode('ascii', 'ignore')
	if received_flag == flag:
		exit(OK)
	print("Received invalid flag '%s' != '%s'" % (received_flag, flag), file=stderr)
	exit(CORRUPT)

def info(*args):
	print("vulns: 1")
	exit(OK)


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    close(CHECKER_ERROR)


if __name__ == '__main__':
	try:
		COMMANDS.get(argv[1], not_found)(*argv[2:])
	except Exception as e:
		print(e, file=stderr)
		exit(CHECKER_ERROR)

