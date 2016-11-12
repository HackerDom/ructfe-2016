#!/usr/bin/env python3

from sys import argv, stderr
from urllib.error import URLError as http_error
from urllib.request import Request, urlopen
from socket import error as network_error
import urllib
import json
import string
import random

from maps_generator import SeafloorMap, SeafloorMapsGenerator

import UserAgents

__author__ = 'm_messiah, tris, dodo_888'

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

FLAGS_ALPHABET = string.ascii_uppercase + string.digits

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
        data = json.dumps({'key': key, 'id': id}).encode('utf-8')
        return self.request("POST", "images/decrypt", lambda res: res, json=data)

    def postImage(self, image):
        return self.request("POST", "images/encrypt", lambda res: json.loads(res.decode('utf-8')), data=image)

    def putChunk(self, chunkid, chunk):
        return self.request("PUT", "chunks/"+chunkid, lambda res: None, data=chunk)

    def getChunk(self, chunkid):
        return self.request("GET", "chunks/"+chunkid, lambda res: res)

    def getRecentChunks(self):
        return self.request("GET", "chunks/_recent", lambda res: json.loads(res.decode('utf-8')))

    def request(self, method, relative_url, fun, **kwargs):
        data = None
        headers = { "User-Agent": UserAgents.get() }
        if "data" in kwargs:
            headers["Content-Type"] = 'application/octet-stream'
            data = kwargs["data"]
        elif "json" in kwargs:
            headers["Content-Type"] = 'application/json; charset=utf8'
            data = kwargs["json"]

        url = "http://%s/%s" % (self.addr, relative_url)
        request = Request(url, method=method, data=data, headers=headers)
        with urlopen(request) as response:
            if (response.status != 200):
                raise CheckerException("Recieved status %d on request %s" % (response.status, url))
            return fun(response.read())


class CheckerException(Exception):
    """Custom checker error"""
    def __init__(self, msg):
        super(CheckerException, self).__init__(msg)


def try_put(client, flag):
    generator = SeafloorMapsGenerator()
    seafloorMap = generator.generate()
    seafloorMap.addFlag(flag)
    postResult = client.postImage(seafloorMap.toBytes())
    metadata = postResult
    if not check_chunk_in_recent(client, metadata["id"]):
        raise CheckerException("Chunk that was just put is not among recent")
    return metadata


def put(*args):
    addr = args[0]
    flag_id = args[1]
    flag = args[2]
    client = Client(addr)   
    try:
        put_result = try_put(client, flag)
        close(OK, json.dumps(put_result))
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(MUMBLE, "Unknown error", "Unknown error: %s" % e)


def check_chunk_in_recent(client, chunkid):
    chunks = client.getRecentChunks()
    for chunk in chunks:
        if chunk == chunkid:
            return True
    return False


def try_get(client, flag, metadata):
    image = client.getImage(metadata["key"], metadata["id"])
    seafloorMap = SeafloorMap.fromBytes(image)
    if seafloorMap.getFlag() != flag:
        close(CORRUPT, "Flag is missing")


def get(*args):
    addr = args[0]
    flag = args[2]
    client = Client(addr)
    try:
        metadata = json.loads(args[1])
        try_get(client, flag, metadata)
        close(OK)
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Network Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(MUMBLE, "Unknown error", "Unknown error: %s" % e)


def check(*args):
    addr = args[0]
    client = Client(addr)
    flag = "".join([ random.choice(FLAGS_ALPHABET) for _ in range(31) ]) + "="
    try:
        metadata = try_put(client, flag)
        try_get(client, flag, metadata)
        close(OK)
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(MUMBLE, "Unknown error", "Unknown error: %s" % e)


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
        close(CHECKER_ERROR, "Cute checker :3", "INTERNAL ERROR: %s" % e)

if __name__ == '__main__':
    main()
