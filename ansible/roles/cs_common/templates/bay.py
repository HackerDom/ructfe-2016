#!/usr/bin/env python3

import os
import socket
import sys
import traceback
import re
import random

PORT = 8888

NOP_COUNT = 8
MSG_OUT_SIZE = 1000

OK, GET_ERROR, CORRUPT, FAIL, INTERNAL_ERROR = 101, 102, 103, 104, 110

def readline(s):
    chars = []
    while True:
        a = s.recv(1)
        chars.append(a)
        if not a or a == b"\n":
            return b"".join(chars)


def pad_and_send(s, msg):
    l = int(MSG_OUT_SIZE)
    if len(msg) < l:
        msg += " " + "A" * (l - len(msg) - 1)
    msg += "\n"
    s.sendall(msg.encode())


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    exit(code)

class CheckerException(Exception):
    """Custom checker error"""
    def __init__(self, msg):
        super(CheckerException, self).__init__(msg)

def hello_data_exchange(s):
    hello_re = rb"\+ I've got (\d+) flags"
    flags_num = int(re.match(hello_re, readline(s).strip()).group(1))

    for i in range(NOP_COUNT):
        pad_and_send(s, "nop")
        readline(s)


def check(addr):
    s = socket.create_connection((addr, PORT))
    hello_data_exchange(s)

    close(OK)        


def put(addr, flag_id, flag):
    s = socket.create_connection((addr, PORT))
    hello_data_exchange(s)

    pad_and_send(s, "put %s %s" % (flag_id, flag))
    if not readline(s).startswith(b"+ ok"):
        close(FAIL, "Failed to put the flag", "Failed to put the flag")

    close(OK, flag_id)


def get(addr, checker_flag_id, flag):
    s = socket.create_connection((addr, PORT))
    hello_data_exchange(s)

    pad_and_send(s, "check %s %s" % (checker_flag_id, flag))
    if not readline(s).startswith(b"+ ok"):
        close(GET_ERROR, "Failed to get the flag", "Failed to get the flag")   

    close(OK)


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    close(INTERNAL_ERROR, "Checker error", "Unsupported command %s" % sys.argv[1] )


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], not_found)(*sys.argv[2:])
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except OSError as e:
        close(CORRUPT, "Socket I/O error", "SOCKET ERROR: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "INTERNAL ERROR: %s" % e)

