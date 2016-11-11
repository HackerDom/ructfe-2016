#!/usr/bin/python3

from base64 import b64encode, b64decode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from struct import pack, unpack
from Crypto.Cipher import AES
from PIL import Image, PngImagePlugin
import json
import codecs
import io

def image_from_bytes(byteArr):
    return Image.open(io.BytesIO(byteArr))

def get_flags_from_image(image):
    return image.info["additionalInfo"]

def decrypt(key, data):
    cipher = AES.new(bytes(key), AES.MODE_CBC, bytes(key))
    return cipher.decrypt(bytes(data))[:-7]

def decrypt_chunk(key, chunk):
    length = unpack(">L", chunk[:4])[0]
    metadata_encrypted = chunk[4:4 + length]
    metadata_str = decrypt(key, metadata_encrypted).decode('ascii')
    print(metadata_str)
    metadata = json.loads(metadata_str)
    session_key = b64decode(metadata["sessionKey"])
    return decrypt(session_key, chunk[4 + length:])

def get_chunk(host, id):
    url = "http://%s/chunks/%s" % (host, id)

    with urlopen(url) as response:
        chunk = response.read()

    return chunk

if __name__ == '__main__':
    import sys

    if not sys.argv[3:]:
        print('Usage: %s <host> <key> <id>' % (sys.argv[0], ))
        sys.exit(1)

    host = sys.argv[1]
    key = codecs.decode(sys.argv[2].encode('ascii'), 'hex')
    id = sys.argv[3]

    chunk = get_chunk(host, id)
    image_bytes = decrypt_chunk(key, chunk)
    image = image_from_bytes(image_bytes)
    flag = get_flags_from_image(image)

    print(flag)
