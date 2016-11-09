#!/usr/bin/env python3

from sys import argv, stderr
from urllib.error import URLError as http_error
from socket import error as network_error
import urllib
import requests
import grequests
import json
import string
import random
import time

from maps_generator import SeafloorMap, SeafloorMapsGenerator

import UserAgents

__author__ = 'm_messiah, tris, dodo_888'

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

FLAGS_ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits

NECESSARY_TIME_DIFFERENCE = 5 * 60

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
        data = {'key': key, 'id': id}
        return self.request("POST", "images/decrypt", lambda res: res.content, json=data)

    def postImage(self, image):
        return self.request("POST", "images/encrypt", lambda res: res.json(), data=image)

    def putChunk(self, chunkid, chunk):
        return self.request("PUT", "chunks/"+chunkid, lambda res: None, data=chunk)

    def getChunk(self, chunkid):
        return self.request("GET", "chunks/"+chunkid, lambda res: res.content)

    def request(self, method, relative_url, fun, **kwargs):
        headers = kwargs.get("headers", {})
        headers["User-Agent"] = UserAgents.get()
        kwargs["headers"] = headers

        response = requests.request(method, "http://%s/%s" % (self.addr, relative_url), **kwargs)
        if (response.status_code != 200):
            raise CheckerException("Recieved status %d on request %s"
                % (response.status_code, response.url))
        return fun(response)

class CheckerException(Exception):
    """Custom checker error"""
    def __init__(self, msg):
        super(CheckerException, self).__init__(msg)


def try_put(client, flag):
    generator = SeafloorMapsGenerator()
    seafloorMap = generator.generate()
    seafloorMap.addFlag(flag)
    postResult = client.postImage(seafloorMap.toBytes())
    postResult['time'] = time.time()
    print(json.dumps(postResult))


def put(*args):
    addr = args[0]
    flag_id = args[1]
    flag = args[2]
    client = Client(addr)
    try:
        put_result = try_put(client, flag)
        close(OK, put_result)
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def try_get(client, flag, metadata):
    image = client.getImage(metadata["key"], metadata["id"])
    seafloorMap = SeafloorMap.fromBytes(image)
    if (seafloorMap.getFlag() != flag):
        raise CheckerException("Didn't find posted flag")
    # check replicas
    # close(CORRUPT, "Flag is missing from all replicas")

def check_replicas(client, flag, me):


def get(*args):
    addr = args[0]
    metadata = json.loads(args[1])
    if (time.time() - metadata['time'] < NECESSARY_TIME_DIFFERENCE):
        close(OK)
    flag = args[2]
    client = Client(addr)
    try:
        try_get(client, flag, metadata)
        close(OK)
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Network Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def check(*args):
    addr = args[0]
    client = Client(addr)
    flag = "".join([ random.choice(FLAGS_ALPHABET) for _ in range(31) ]) + "="
    try:
        metadata = try_put(client, flag)
        try_get(client, flag, json.loads(metadata))
        close(OK)
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
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
        close(CHECKER_ERROR, "MY DICK IS BIG, IT'S VERY VERY BIG", "INTERNAL ERROR: %s" % e)
    
if __name__ == '__main__':
    main()