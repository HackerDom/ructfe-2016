#!/usr/bin/env python3

from sys import argv, stderr
import subprocess
import socket
import random
import string

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

def control(target, request, do_receive):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	data = None

	try:
		s.connect((target, 16761))
	except:
		print("Failed to connect to control port", file=stderr)
		exit(DOWN)

	try:
		s.sendall(request)
		if do_receive:
			data = s.recv(1024)
			if b"502 Bad Gateway" in data:
				print("Got 502 from nginx", file=stderr)
				exit(DOWN)

	except Exception as e:
		print("Failed to communicate through control port: " + str(e), file=stderr)
		exit(DOWN)

	s.close()

	return data

def check(*args):
	addr, = args

	data = str(random.random())[2:]
	signature = subprocess.check_output('./signtool ' + data, shell=True).strip().decode('ascii')

	request = b'/' + data.encode('ascii') + b'\n'

	data = control(addr, request, True)

	text = data.decode('ascii', 'ignore')

	if not "Signature: " + signature in text:
		print("Forecast does not contain valid signature", file=stderr)
		exit(MUMBLE)

	exit(OK)

def put(*args):
	addr, flag_id, flag, *vuln = args

	flag_id = ''.join([random.choice(string.ascii_lowercase) for _ in range(12)])

	request = b'\x01\x00\x00\x00' + flag_id.replace('-', '').encode('ascii') + flag.encode('ascii')

	control(addr, request, False)

	print(flag_id)

	exit(OK)

def get(*args):
	addr, flag_id, flag, *vuln = args

	request = b'\x00\x00\x00\x00' + flag_id.replace('-', '').encode('ascii')

	data = control(addr, request, True)

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

