#!/usr/bin/env python3
from __future__ import print_function
from sys import argv, stderr
import os
import zipfile
import subprocess
import requests


SERVICE_NAME = "submarine_internal"
PORT = 1080
OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=stderr)
    print('Exit with code %d' % code, file=stderr)
    exit(code)


def check(*args):
	close(OK)


def put(*args):
	addr = args[0]
	flag_id = args[1]
	flag = args[2]

	# crash the binary and generate minidump
	cmdLine = './%s %s' % ( SERVICE_NAME, flag )
	try:
		minidumpFilePath = subprocess.check_output( cmdLine, shell=True)
	except subprocess.CalledProcessError as e:
		minidumpFilePath = e.output
	minidumpFileName = minidumpFilePath[6:] # skip dumps/
	guid = os.path.splitext(minidumpFileName)[0]

	# zip minidump file
	zipFilePath = "zips/" + flag_id + ".zip"
	zf = zipfile.ZipFile( zipFilePath, mode='w')
	try:
		zf.write( minidumpFilePath, arcname = '%s.dmp' % flag_id )
	except Exception as e:
		close(CHECKER_ERROR, "ZIP error", "Unknown error: %s" % e)
	zf.close()

	# submit report
	url = 'http://%s:%s/submit' % ( addr, PORT )
	files = { 'dump_zip_file': open( zipFilePath, 'rb' ) }
	headers = { 'service_name' : SERVICE_NAME, 'guid' : flag_id }
	try:
		requests.post(url, files=files, headers=headers )
	except Exception as e:
		 close(DOWN, "HTTP Error", "HTTP error sending to '%s'" % addr)
	close(OK)


def get(*args):
	close(OK)


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR


if __name__ == '__main__':
    try:
        COMMANDS.get(argv[1], not_found)(*argv[2:])
    except Exception as e:
        close(CHECKER_ERROR, "Evil checker", "INTERNAL ERROR: %s" % e)

