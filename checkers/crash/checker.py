#!/usr/bin/python
import sys
import os
import zipfile
import subprocess
import requests
import md5
from time import gmtime, strftime

SERVICE_NAME = "test_app"

flag = sys.argv[ 1 ]
ip = sys.argv[ 2 ]
port = 1080

# crash the binary and generate minidump
dmpFilePath = ""
cmdLine = './%s %s' % ( SERVICE_NAME, flag )
try:
	dmpFilePath = subprocess.check_output( cmdLine, shell=True)
except subprocess.CalledProcessError as e:
	dmpFilePath = e.output

# zip minidump file
print dmpFilePath
dmpFileName = dmpFilePath[6:] # skip dumps/
guid = os.path.splitext(dmpFileName)[0]
zipFilePath = "zips/" + guid + ".zip"

# submit zip file
zf = zipfile.ZipFile( zipFilePath, mode='w')
try:
    zf.write( dmpFilePath, arcname = dmpFileName )
finally:
    zf.close()

# generate pseudo flag id
m = md5.new()
m.update( strftime("%M%S", gmtime() ) )
flag_id = m.hexdigest()

# submit report
url = 'http://%s:%s/submit' % ( ip, port )
files = { 'dump_zip_file': open( zipFilePath, 'rb' ) }
headers = { 'service_name' : SERVICE_NAME, 'guid' : guid, 'secret_id' : flag_id }
r = requests.post(url, files=files, headers=headers )
r.text

