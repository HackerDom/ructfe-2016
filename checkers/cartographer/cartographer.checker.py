#!/usr/bin/env python3
# coding=utf-8
from __future__ import print_function
from sys import argv, stderr
from urllib.error import URLError as http_error
import urllib
import requests
from socket import error as network_error
import maps_generator
import json

__author__ = 'm_messiah'

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=stderr)
    print('Exit with code %d' % code, file=stderr)
    exit(code)

class Client(object):
    def __init__(self, addr):
        self.addr = addr

    def getImage(self, key, id):
        headers = {'content-type': 'application/json'}
        data = {'key': key, 'id': id}
        response = requests.post("http://%s/%s" % (self.addr, "images/decrypt"), json=data, headers=headers)
        if (response.status_code != 200):
            raise CheckerException("Recieved status %d on request %s"
                % (response.status_code, response.url))
        return response.content

    def postImage(self, image):
        response = requests.post("http://%s/%s" % (self.addr, "images/encrypt"), data=image)
        if (response.status_code != 200):
            raise CheckerException("Recieved status %d on request %s"
                % (response.status_code, response.url))
        return response.json()

    def putChunk(self, chunkid, chunk):
        response = requests.post("http://%s/%s" % (self.addr, "chunks/"+chunkid), data=chunk)
        if (response.status_code != 200):
            raise CheckerException("Recieved status %d on request %s"
                % (response.status_code, response.url))

    def getChunk(self, chunkid):
        response = requests.post("http://%s/%s" % (self.addr, "chunks/"+chunkid))
        if (response.status_code != 200):
            raise CheckerException("Recieved status %d on request %s"
                % (response.status_code, response.url))
        return response.content

class CheckerException(Exception):
    """Custom checker error"""
    def __init__(self, msg):
        super(CheckerException, self).__init__(msg)


def check(*args):
    addr = args[0]
    client = Client(addr)
    flag = "justastrangecombinationofwords"
    try:
        generator = maps_generator.SeafloorMapsGenerator()
        seafloorMap = generator.generate()
        seafloorMap.addFlag(flag)
        postResult = client.postImage(seafloorMap.toBytes())
        byteArr = client.getImage(postResult['key'], postResult['id'])
        seafloorMap = seafloorMap.fromBytes(byteArr)
        if (seafloorMap.getFlag() != flag):
            raise CheckerException("Didn't find posted flag")
        close(OK)
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def put(*args):
    addr = args[0]
    flag_id = args[1]
    flag = args[2]
    client = Client(addr)
    try:
        generator = maps_generator.SeafloorMapsGenerator()
        seafloorMap = generator.generate()
        seafloorMap.addFlag(flag)
        postResult = client.postImage(seafloorMap.toBytes())
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)
    return json.dumps(postResult)


def get(*args):
    addr = args[0]
    checker_flag_id = json.loads(args[1])
    flag = args[2]
    client = Client(addr)
    try:
        image = client.getImage(checker_flag_id.key, checker_flag_id.id)
        seafloorMap = SeafloorMap.fromBytes(image)
        if (seafloorMap.getFlag() != flag):
            raise CheckerException("Didn't find posted flag")
        #check replicas
        close(CORRUPT, "Flag is missing")
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Network Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def info(*args):
    close(OK, "vulns: 1")

HANDLERS = {'check': check, 'put': put, 'get': get, 'info': info}

def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR


def main():
    try:
        HANDLERS.get(argv[1], not_found)(*argv[2:])
    except Exception as e:
        close(CHECKER_ERROR, "Sweet and cute checker =3", "INTERNAL ERROR: %s" % e)
    
if __name__ == '__main__':
    main()