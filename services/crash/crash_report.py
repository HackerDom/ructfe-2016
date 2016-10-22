#!/usr/bin/python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
import zipfile
from time import gmtime, strftime
import sqlite3

sqliteConn = sqlite3.connect( 'reports.db' )


SERVICES = [ "test_app" ]
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
		name = os.path.basename(info.filename)
		if name == '':
			# skip directories
			continue
		
		try:
			data = zf.read(info.filename)
			new_name = os.path.join(extract_path, name)
			open(new_name, "wb").write(data)
		except:
			pass

	return True


class RequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):

        self.send_response(404)
        
    def do_POST(self):
        
        request_path = self.path
        if request_path == '/submit':
        	if self.SubmitHandler():
        		self.send_response(200)
        	else:
        		self.send_response(404)
        else:
        	self.send_response(404)

    def SubmitHandler(self):
    	try:
    		request_headers = self.headers
        	form = cgi.FieldStorage(
            				fp = self.rfile,
            				headers = self.headers,
            				environ = {'REQUEST_METHOD':'POST',
                     			'CONTENT_TYPE' : self.headers['Content-Type'],
                     			})
        	if 'dump_zip_file' not in form:
        		print "There is no dump_zip_file in request"
        		return False

        	try:
        		service_name = request_headers.getheaders( 'service_name' )[ 0 ]
        		guid = request_headers.getheaders( 'guid' )[ 0 ]
        		secret_id = request_headers.getheaders( 'secret_id' )[ 0 ]
        	except:
        		print "There is no service name or guid in headers"
        		return False

        	if service_name not in SERVICES:
        		print 'Unknown service %s' % service_name
        		return False

        	zipFileData = form[ 'dump_zip_file' ].file.read()

        	print 'Crash repot for %s GUID %s ID %s' % ( service_name, guid, secret_id )

		cur_time = gmtime()
		cur_date_dir = os.path.join( REPORTS_DIR, strftime("%Y/%m/%d", cur_time ) )
        	if not os.path.exists(cur_date_dir):
        		if not create_dir(cur_date_dir):
				print 'Can not create dir %s' % cur_date_dir
				return False

        	report_dir = os.path.join( cur_date_dir, guid )
        	if not os.path.exists(report_dir):
			if not create_dir(report_dir):
				print 'Can not create dir %s' % report_dir
				return False
		else:
			print 'Report %s already exists, it will be overwritten' % report_dir

		report_name = os.path.join(report_dir, "minidump.zip")
		try:
			f = open( report_name, "wb" )
			f.write( zipFileData )
			f.close()
		except:
			print 'Failed to save file %s' % report_name
			return False

		if not safe_extract_zip( report_name, report_dir ):
			print 'Failed to extract zip file'
			return False

		dump_name = os.path.join(report_dir, guid + ".dmp")
		if not os.path.exists( dump_name ):
			print 'Where is minidump file?'
			return False

		try:
			# google-breakpad/src/processor/minidump_stackwalk minidump.dmp ./symbols
			TOOL_NAME = "./minidump_stackwalk"
			STACKWALK_FILENAME = os.path.join( report_dir, "stackwalk.txt" )
			STACKWALK_ERRORS_FILENAME = os.path.join( report_dir, "stackwalk_errors.txt" )
			result = os.system('%s -m %s %s >%s 2>%s' % (TOOL_NAME, dump_name, SYMBOLS_DIR, STACKWALK_FILENAME, STACKWALK_ERRORS_FILENAME))
			if result != 0:				
				print 'stack walk failed: %d' % result
				return False
		except:
			print 'stack walk failed'
			return False

		cursor = sqliteConn.cursor()
		row = ( service_name, guid, secret_id )
		cursor.execute( "INSERT INTO reports VALUES ( ?, ?, ? )", row )
		sqliteConn.commit()

        	return True

	except:
		print 'Something went wrong'
		return False
    
    do_PUT = do_POST
    do_DELETE = do_GET
    
port = 1080
print('Listening on localhost:%s' % port)
server = HTTPServer(('', port), RequestHandler)
server.serve_forever()
