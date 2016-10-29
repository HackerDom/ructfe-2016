#!/usr/bin/python
import sys
from bottle import get, post, request, run, static_file, response
import os
import zipfile
from time import gmtime, strftime
import sqlite3
import re
import json
from stack_walk_parser import StackWalkParser
#[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{8}-[0-9a-z]{8}

sqliteConn = sqlite3.connect( 'reports.db' )

REPORTS_DIR = "reports/"
SYMBOLS_DIR = "symbols/"


def create_dir(name):
	if not os.path.exists(name):
		try:
			os.makedirs(name)
		except:
			return False

	if not os.path.isdir(name):
		return False

	return True


def safe_extract_zip(file_name, extract_path):
	if not os.path.exists(extract_path):
		return False

	if not zipfile.is_zipfile(file_name):
		return False

	zf = zipfile.ZipFile(file_name, "r")
	for info in zf.infolist():
		try:
			data = zf.read(info.filename)
			new_name = os.path.join(extract_path, info.filename)
			create_dir( os.path.dirname( new_name ) )
			if not os.path.exists( new_name ):
				open(new_name, "wb").write(data)
		except:
			pass

	return True


@get('/')
def Index():
	cursor = sqliteConn.cursor()
	reports = []
	for row in cursor.execute( "SELECT * FROM reports" ):
		report = { "guid" : row[ 0 ], "service_name:" : row[ 1 ], "signature" : row[ 2 ], "time" : row[ 3 ] }
		reports.append( report )
	return json.dumps( reports )


@get('/<guid:re:[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}>')
def DumpDetailHandler(guid):
	report_dir = os.path.join( REPORTS_DIR, guid )
	stackwalk_file = os.path.join( report_dir, "stackwalk.txt" )
	parser = StackWalkParser()
	parser.parse( stackwalk_file )			
	dump_detail = { "crash_reason" : parser.crash_reason, "crash_address" : parser.crash_address, "crash_thread_stack" : parser.crash_thread_stack }
	return json.dumps( dump_detail )


@get('/<guid:re:[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}>/get')
def GetDumpHandler(guid):
	report_dir = os.path.join( REPORTS_DIR, guid )
	f = open( os.path.join( report_dir, "minidump.zip" ), 'rb' )
	zipdata = f.read()
	f.close
	response.content_type = "application/zip"
	response.add_header('Content-Disposition', 'attachment; filename=%s.zip;' % guid )	
	return zipdata


@post('/submit')
def SubmitHandler():
	try:
	  	dump_zip_file = request.files.get('dump_zip_file')
		if not dump_zip_file:
	  		print "There is no dump_zip_file in request"
	  		return json.dumps( { 'status' : 'fail' } )
		zipFileData = dump_zip_file.file.read()

  		service_name = request.headers.get( 'service_name' )
  		guid = request.headers.get( 'guid' )
		if not guid or not service_name:
			print "There is no service name or guid in headers"
		  	return json.dumps( { 'status' : 'fail' } )

		if not re.match( r'^[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}$', guid):
			print "Strange guid"
			return json.dumps( { 'status' : 'fail' } )

		if not re.match( r'^[0-9a-zA-Z_]+$', service_name):
			print "Strange service name"
			return json.dumps( { 'status' : 'fail' } )

	  	print 'Crash repot for %s GUID %s' % ( service_name, guid )

	  	report_dir = os.path.join( REPORTS_DIR, guid )
	  	if os.path.exists(report_dir):
			print 'Report %s already exists' % report_dir
			return json.dumps( { 'status' : 'fail' } )

		if not create_dir(report_dir):
			print 'Can not create dir %s' % report_dir
			return json.dumps( { 'status' : 'fail' } )

		report_name = os.path.join(report_dir, "minidump.zip")
		try:
			f = open( report_name, "wb" )
			f.write( zipFileData )
			f.close()
		except:
			print 'Failed to save file %s' % report_name
			return json.dumps( { 'status' : 'fail' } )

		if not safe_extract_zip( report_name, report_dir ):
			print 'Failed to extract zip file'
			return json.dumps( { 'status' : 'fail' } )

		dump_name = os.path.join(report_dir, guid + ".dmp")
		if not os.path.exists( dump_name ):
			print 'Where is minidump file?'
			return json.dumps( { 'status' : 'fail' } )

		try:
			# google-breakpad/src/processor/minidump_stackwalk minidump.dmp ./symbols
			TOOL_NAME = "./minidump_stackwalk"
			STACKWALK_FILENAME = os.path.join( report_dir, "stackwalk.txt" )
			STACKWALK_ERRORS_FILENAME = os.path.join( report_dir, "stackwalk_errors.txt" )
			result = os.system('%s -m %s %s >%s 2>%s' % (TOOL_NAME, dump_name, SYMBOLS_DIR, STACKWALK_FILENAME, STACKWALK_ERRORS_FILENAME))
			if result != 0:				
				print 'stack walk failed: %d' % result
				return json.dumps( { 'status' : 'fail' } )

			parser = StackWalkParser()
			parser.parse( STACKWALK_FILENAME )			
		except:
			print 'stack walk failed'
		  	return json.dumps( { 'status' : 'fail' } )

		cursor = sqliteConn.cursor()
		row = ( guid, service_name, parser.signature, strftime("%H %M %S", gmtime() ) )
		cursor.execute( "INSERT INTO reports VALUES ( ?, ?, ?, ? )", row )
		sqliteConn.commit()

	  	return json.dumps( { 'status' : 'ok' } )

	except:
		print 'Something went wrong'
		return False
    

run(host='0.0.0.0', port=1080)
