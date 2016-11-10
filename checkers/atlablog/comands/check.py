from comands import OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR
from templates.user_credentials import generate_user_credentials

from urllib.request import Request, build_opener, HTTPCookieProcessor, HTTPRedirectHandler
from urllib.parse import quote
from urllib.error import HTTPError
import re
import string
import random


def non_selenium_check(command_ip):
    browser = build_opener(
        HTTPCookieProcessor,
        HTTPRedirectHandler
    )
    username, password, email = generate_user_credentials()
    data = {
        "username": username,
        "password": password,
        "email": email,
        "accept_rules": "y"
    }

    data = ["{}={}".format(key, quote(data[key])) for key in data]

    request = Request(url="http://{}/registration".format(command_ip))
    request.method = "POST"
    request.data = bytes("&".join(data), "utf-8")
    try:
        response = browser.open(request, timeout=5).read().decode()
    except HTTPError:
        return {
            "code": DOWN,
            "public": "Service timed out"
        }
    except ValueError:
        return {
            "code": MUMBLE,
            "public": "Can't check public api!"
        }
    except KeyError:
        return {
            "code": MUMBLE,
            "public": "Can't use public api!"
        }
    links = re.findall(r'(?<=href=\").*(?=\"><h2>)', response)
    if not links:
        return {
            "code": MUMBLE,
            "public": "Can't find any post!"
        }

    request = Request(url="http://{}{}".format(command_ip, links[0]))
    request.method = "POST"
    comment = random.sample(
        list(string.ascii_lowercase) * 10, random.randint(30, 60)
    )

    data = {
        "text": "".join(comment),
        "attachments": ''
    }
    data = ["{}={}".format(key, quote(data[key])) for key in data]
    request.data = bytes("&".join(data), "utf-8")
    try:
        response = browser.open(request, timeout=5).read().decode()
        if "".join(comment) in response:
            return {
                "code": OK
            }
    except HTTPError:
        return {
            "code": MUMBLE,
            "public": "Can't post comment!"
        }


