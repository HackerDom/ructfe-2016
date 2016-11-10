from comands import OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR
from templates.user_credentials import generate_user_credentials

from urllib.request import Request, build_opener, HTTPCookieProcessor, HTTPRedirectHandler
from urllib.parse import quote
from urllib.error import HTTPError
import random
import string
import re


def non_selenium_put(command_ip, flag_id, flag, vuln):
    browser = build_opener(
        HTTPCookieProcessor,
        HTTPRedirectHandler
    )
    username, password, email = generate_user_credentials(flag)
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

    request = Request(url="http://{}".format(command_ip))
    request.method = "POST"
    title = "".join(random.sample(
        list(string.ascii_lowercase) * 10, random.randint(15, 20)
    ))
    post_text = "".join(random.sample(
        list(string.ascii_lowercase) * 10, random.randint(30, 60)
    ))

    data = {
        "title": title,
        "text": post_text,
        "attachments": ''
    }
    data = ["{}={}".format(key, quote(data[key])) for key in data]
    request.data = bytes("&".join(data), "utf-8")
    try:
        response = browser.open(request, timeout=5).read().decode()
    except HTTPError:
        return {
            "code": MUMBLE,
            "public": "Can't post comment!"
        }

    links = re.findall(r'(?<=href=\").*(?=\"><h2>)', response)
    for link in links:
        if "/" + title in link.split("-")[0]:
            return {
                "code": OK,
                "flag_id": "{}:{}:{}".format(username, password, title)
            }

    return {
        "code": MUMBLE,
        "public": "Can't find checksystem post! {}".format("|".join(links))
    }