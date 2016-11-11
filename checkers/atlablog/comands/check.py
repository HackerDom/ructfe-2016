from comands import OK, MUMBLE, DOWN
from templates.urllib_forms import \
    MumbleException, DownException, try_register_user, try_make_post, get_useragent

from urllib.request import Request, build_opener, HTTPCookieProcessor, \
    HTTPRedirectHandler
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
    try:
        try_register_user(browser, command_ip)
        title, response = try_make_post(browser, command_ip)

        post_links = re.findall(r'(?<=href=\").*(?=\"><h2>)', response)
        if not post_links:
            raise MumbleException("Can't find any post!")

        try_register_user(browser, command_ip)
        request = Request(url="http://{}{}".format(command_ip, post_links[0]))
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
        request.add_header('User-Agent', get_useragent())
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

    except MumbleException as e:
        return {
            "code": MUMBLE,
            "public": str(e)
        }

    except DownException as e:
        return {
            "code": DOWN,
            "public": str(e)
        }