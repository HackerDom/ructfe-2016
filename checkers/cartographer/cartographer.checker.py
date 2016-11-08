#!/usr/bin/env python3
# coding=utf-8
from __future__ import print_function
from sys import argv, stderr
from urllib.error import URLError as http_error
import requests
from socket import error as network_error
import maps_generator

__author__ = 'm_messiah'

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
	
if __name__ == '__main__':
    close(OK)