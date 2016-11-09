#!/usr/bin/env python3

from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from json import dumps
from binascii import hexlify, unhexlify

import checker

class Signer:
	def __init__(self):
		with open('id_rsa') as keyFile:
			keyString = keyFile.read()
		key = RSA.importKey(keyString)
		self.signer = PKCS1_PSS.new(key)
	def getHash(self, hostname, username, data):
		request = {'title': data['title'], 'body': data['body'], 'hostname': hostname, 'username': username}
		message = dumps(request, sort_keys=True)
		h = SHA256.new()
		h.update(message.encode('utf-8'))
		return h
	def sign(self, hostname, username, data):
		h = self.getHash(hostname, username, data)
		sign = self.signer.sign(h)
		return hexlify(sign).decode()
	def check(self, hostname, username, data):
		h = self.getHash(hostname, username, data)
		if 'sign' not in data:
			checker.mumble(error='fail to find sign')
		try:
			sign = unhexlify(data['sign'].encode())
		except Exception as ex:
			checker.mumble(error='fail to parse sign', exception=ex)
		return self.signer.verify(h, sign)

