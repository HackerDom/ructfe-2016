from templates.user_credentials import generate_user_credentials
from urllib.request import Request
from urllib.parse import quote
import re
from urllib.error import HTTPError
import random
import string


def try_register_user(browser, command_addr, email=""):
    for i in range(2):
        username, password, email, response = __register_user(browser, command_addr, email)
        if not re.findall(r'(?<=class=\"errors\"><li>)Username already used(?=</li></ul>)',response):
            return username, password, email, response
    raise MumbleException("Can't register user!")


def try_make_post(browser, command_addr):
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

    request = prepare_post_request(command_addr, data)
    try:
        response = browser.open(request, timeout=5).read().decode()
        return title, response
    except HTTPError:
        raise MumbleException("Can't make checksystem's post!")


def __register_user(browser, command_addr, email):
    username, password, email = generate_user_credentials(email)
    data = {
        "username": username,
        "password": password,
        "email": email,
        "accept_rules": "y"
    }

    request = prepare_post_request(command_addr + "/registration", data)

    try:
        response = browser.open(request, timeout=5).read().decode()
        return username, password, email, response
    except HTTPError:
        raise DownException("Service timed out!")
    except ValueError:
        raise MumbleException("Can't check public api!")
    except KeyError:
        raise MumbleException("Can't check public api!")


def prepare_post_request(url, data):
    data = ["{}={}".format(key, quote(data[key])) for key in data]

    request = Request(url="http://{}".format(url))
    request.method = "POST"
    request.data = bytes("&".join(data), "utf-8")
    return request


class DownException(Exception):
    pass


class MumbleException(Exception):
    pass
