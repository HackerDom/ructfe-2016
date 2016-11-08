#!/usr/bin/python
import sys
import os
import zipfile
import requests
from io import BytesIO

PORT = 1080
addr = sys.argv[1]
guid = sys.argv[2]

# zip minidump file
inMemoryZip = BytesIO()
zf = zipfile.ZipFile( inMemoryZip, mode='w' )
zf.write( "dump.dmp", arcname = '%s.dmp' % guid )
zf.write( "symbols/just_crash/8A0D3C1EADB4865FDC91DA786A0E07640/just_crash.sym", "../../symbols/just_crash/8A0D3C1EADB4865FDC91DA786A0E07640/just_crash.sym" )
zf.close()
inMemoryZip.seek(0)

# submit report
url = 'http://%s:%s/submit' % ( addr, PORT )
print url
files = { 'dump_zip_file': inMemoryZip.read() }
headers = { 'Service-Name' : "just_crash", 'GUID' : guid }
requests.post(url, files=files, headers=headers )
