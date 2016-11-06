#!/usr/bin/python
import sys
from bottle import get, post, request, run, static_file, response, route, template
import os
import zipfile
from time import gmtime, strftime
import sqlite3
import re
import json
from stack_walk_parser import StackWalkParser
from io import BytesIO
#[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{8}-[0-9a-z]{8}

sqliteConn = sqlite3.connect( 'reports.db' )

REPORTS_DIR = "reports/"
SYMBOLS_DIR = "symbols/"


@route('/static/<filepath:path>')
def static(filepath):
	return static_file(filepath, root='./static/')

@route('/')
def main_page():
	return template('main_page.tpl')

@route('/report.html')
def main_page():
    return template('report.tpl')


def create_dir(name):
	if not os.path.exists(name):
		try:
			os.makedirs(name)
		except:
			return False

	if not os.path.isdir(name):
		return False

	return True


def safe_extract_zip(zip_bytes, extract_dir):
	if not os.path.exists(extract_dir):
		return False

	try:
		zf = zipfile.ZipFile( BytesIO( zip_bytes ) )
		filesList = open( os.path.join( extract_dir, ".files_list" ), 'w' )
		for info in zf.infolist():
			try:
				data = zf.read(info.filename)
				file_path = os.path.join(extract_dir, info.filename)
				create_dir( os.path.dirname( file_path ) )
				if not os.path.exists( file_path ):
					open(file_path, "wb").write(data)
				filesList.write( info.filename + '\n' )
			except:
				pass
		filesList.close()
		zf.close()
	except:
		return False	

	return True

@get('/crashes')
def Index():
	cursor = sqliteConn.cursor()
	reports = []
	for row in cursor.execute( "SELECT * FROM reports ORDER BY ROWID DESC LIMIT 50" ):
		guid = row[ 0 ] if re.match( r"^10\.6\d\.\d{1,3}\.\d{1,3}$", request.remote_addr ) else ""
		report = { "guid" : guid, "service_name" : row[ 1 ], "signature" : row[ 2 ], "time" : row[ 4 ] }
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

	inMemoryZip = BytesIO()
	zf = zipfile.ZipFile( inMemoryZip, mode='w')
	for line in open( os.path.join( report_dir, ".files_list" ), 'r' ):
		zf.write( os.path.join( report_dir, line.strip() ), arcname = line.strip() )
	zf.close()
	inMemoryZip.seek(0)

	response.content_type = "application/zip"
	response.add_header('Content-Disposition', 'attachment; filename=%s.zip;' % guid )	
	return inMemoryZip.read()


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

		if not safe_extract_zip( zipFileData, report_dir ):
			print 'Failed to extract zip file'
			return json.dumps( { 'status' : 'fail' } )

		dmp_path = os.path.join(report_dir, guid + ".dmp")
		if not os.path.exists( dmp_path ):
			print 'Where is minidump file?'
			return json.dumps( { 'status' : 'fail' } )

		try:
			# google-breakpad/src/processor/minidump_stackwalk minidump.dmp ./symbols
			TOOL_NAME = "./minidump_stackwalk"
			STACKWALK_FILENAME = os.path.join( report_dir, "stackwalk.txt" )
			STACKWALK_ERRORS_FILENAME = os.path.join( report_dir, "stackwalk_errors.txt" )
			result = os.system('%s -m %s %s >%s 2>%s' % (TOOL_NAME, dmp_path, SYMBOLS_DIR, STACKWALK_FILENAME, STACKWALK_ERRORS_FILENAME))
			if result != 0:
				print 'stack walk failed: %d' % result
				return json.dumps( { 'status' : 'fail' } )

			parser = StackWalkParser()
			parser.parse( STACKWALK_FILENAME )
		except:
			print 'stack walk failed'
			return json.dumps( { 'status' : 'fail' } )

		cursor = sqliteConn.cursor()
		cursor.execute( "INSERT INTO reports VALUES ( '%s', '%s', '%s', '%s', '%s' )" % ( guid, service_name, parser.signature, parser.crash_reason, strftime("%H:%M:%S", gmtime() ) ) )
		sqliteConn.commit()

		return json.dumps( { 'status' : 'ok' } )

	except:
		print 'Something went wrong'
		return False


run(server='tornado', host='0.0.0.0', port=1080, reloader=True)
