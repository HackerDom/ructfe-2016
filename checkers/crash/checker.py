#!/usr/bin/env python3
from __future__ import print_function
from sys import argv, stderr
import os
import zipfile
import subprocess
import requests
from io import BytesIO
from stack_walk_parser import StackWalkParser
import re

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
	inMemoryZip = BytesIO()
	zf = zipfile.ZipFile( inMemoryZip, mode='w' )
	try:
		zf.write( minidumpFilePath, arcname = '%s.dmp' % flag_id )
	except Exception as e:
		close(CHECKER_ERROR, "ZIP error", "Unknown error: %s" % e)
	zf.close()
	inMemoryZip.seek(0)

	# submit report
	url = 'http://%s:%s/submit' % ( addr, PORT )
	files = { 'dump_zip_file': inMemoryZip.read() }
	headers = { 'service_name' : SERVICE_NAME, 'guid' : flag_id }
	try:
		r = requests.post(url, files=files, headers=headers )
		if r.status_code != 200:
			close( MUMBLE, "Submit error", "Invalid status code: %s %d" % ( url, r.status_code ) )	
		r_json = r.json()
		if r_json[ 'status' ] != 'ok':
			close( MUMBLE, "Submit error", "Can not put flag" )
	except Exception as e:
		 close(DOWN, "HTTP Error", "HTTP error: %s" % e)
	close(OK)


def get(*args):
	addr = args[0]
	flag_id = args[1]
	flag = args[2]
	url = 'http://%s:%s/%s/get' % ( addr, PORT, flag_id )
	try:
		r = requests.get( url )
		if r.status_code != 200:
			close( MUMBLE, "Invalid HTTP response", "Invalid status code: %s %d" % ( url, r.status_code ) )	
	except Exception as e:
		 close(DOWN, "HTTP Error", "HTTP error: %s" % e)

	try:
		if int( r.headers[ 'Content-Length' ] ) > 50000: # tested 
			close( CORRUPT, "Service corrupted", "Content is too big" )
	except Exception as e:
		close( CORRUPT, "Service corrupted", "Something wrong with content length: %s" % e )

	# tested
	try:
		zf = zipfile.ZipFile( BytesIO( r.content ) )
	except Exception as e:
		close( CORRUPT, "Service corrupted", "Invalid zip file: %s" % e )

	if len( zf.namelist() ) > 1: # tested
		close( CORRUPT, "Service corrupted", "Invalid content, more than one file in zip" )

	dmp_name = "tmp/%s.dmp" % flag_id
	if not dmp_name in zf.namelist(): # tested
		close( CORRUPT, "Service corrupted", "Invalid content, there is no minidump file in zip" )
	try:
		dmp = zf.read( dmp_name )
		open( dmp_name, 'wb' ).write( dmp )
	except Exception as e:
		close(CHECKER_ERROR, "Evil checker", "INTERNAL ERROR: %s" % e)

	# tested
	try:
		stackwalk = subprocess.check_output( './minidump_stackwalk -m %s symbols/ 2>/dev/null' % dmp_name, shell=True)
	except subprocess.CalledProcessError as e:
		close( CORRUPT, "Service corrupted", "Invalid minidump file: %s" % e )

	parser = StackWalkParser()
	parser.parse( stackwalk.decode() )

	if len( parser.crash_thread_stack) < 17: # not tested
		close( CORRUPT, "Service corrupted", "Invalid minidump file, callstack is too short %s" % parser.crash_thread_stack )
	if len( parser.crash_thread_stack) > 32: # not tested
		close( CORRUPT, "Service corrupted", "Invalid minidump file, callstack is too long" )
	if parser.crash_thread_stack[ 16 ][ "signature" ] != 'main': # tested
		close( CORRUPT, "Service corrupted", "Invalid minidump file, invalid callstack %s" % parser.crash_thread_stack )

	first_part_flag = ''
	for i in reversed( range( 0, 16 ) ): 
		signature = parser.crash_thread_stack[ i ][ "signature" ]
		result = re.match( r"_(\w)\(\)", signature )
		if not result: # tested
			close( CORRUPT, "Service corrupted", "Invalid minidump file, invalid signature in callstack %s" % signature )
		first_part_flag = first_part_flag + result.group(1)

	prefix = b'HERE IS THE REST OF YOUR FLAG'
	prefixPos = dmp.find( prefix )
	if prefixPos == -1:
		close( CORRUPT, "Service corrupted", "Invalid minidump file, cant find second part of the flag" )
	flagPos = prefixPos + len( prefix ) + 1
	try: # tested
		second_part_flag = ( dmp[ flagPos : flagPos + 16 ] ).decode()
	except Exception as e:
		close( CORRUPT, "Service corrupted", "Can not get second part of the flag: %s" % e)

	restored_flag = first_part_flag + second_part_flag
	if flag != restored_flag: # tested
		close( CORRUPT, "Service corrupted", "Flag does not match: %s" % restored_flag )
	close( OK )


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR


if __name__ == '__main__':
	try:
		if not os.path.exists( "dumps/" ):
			os.makedirs( "dumps/" )
		COMMANDS.get(argv[1], not_found)(*argv[2:])
	except Exception as e:
		close(CHECKER_ERROR, "Evil checker", "INTERNAL ERROR: %s" % e)

