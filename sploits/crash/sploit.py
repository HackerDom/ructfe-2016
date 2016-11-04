#!/usr/bin/python
import sys
import os
import zipfile
import requests


PORT = 1080
addr = sys.argv[1]
guid = sys.argv[2]

# zip minidump file
zipFilePath = guid + ".zip"
zf = zipfile.ZipFile( zipFilePath, mode='w')
zf.write( "dump.dmp", arcname = '%s.dmp' % guid )
zf.write( "symbols/just_crash/8A0D3C1EADB4865FDC91DA786A0E07640/just_crash.sym", "../../symbols/just_crash/8A0D3C1EADB4865FDC91DA786A0E07640/just_crash.sym" )
zf.close()

# submit report
url = 'http://%s:%s/submit' % ( addr, PORT )
print url
files = { 'dump_zip_file': open( zipFilePath, 'rb' ) }
headers = { 'service_name' : "just_crash", 'guid' : guid }
requests.post(url, files=files, headers=headers )
