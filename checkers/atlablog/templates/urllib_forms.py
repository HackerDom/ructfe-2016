from templates.user_credentials import generate_user_credentials
from templates.user_agents import get as get_useragent

from urllib.request import Request
from urllib.parse import quote
from urllib.error import HTTPError

import re
import random
import string
import json


def try_register_user(browser, command_addr, email=""):
    for i in range(2):
        username, password, email, response = __register_user(browser, command_addr, email)
        if not re.findall(r'(?<=class=\"errors\"><li>)Username already used(?=</li></ul>)',response):
            return username, password, email, response
    raise MumbleException("Can't register user!")


def try_make_post(browser, command_addr):
    title = random_string(15, 20)
    post_text = random_string(30, 60)
    data = {
        "title": title,
        "text": post_text,
        "attachments": try_upload_file(browser, command_addr)
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


def try_upload_file(browser, command_addr):
    file_stored = random_string(15, 20)
    file_name = random_string(15, 20)
    file_extension = random_string(3, 8)
    request = Request(url="http://{}/upload".format(command_addr))
    request.method = "POST"
    request.data = bytes(file_stored, "utf-8")
    request.add_header('User-Agent', get_useragent())
    request.add_header('X-File-Name', file_name + "." + file_extension)
    try:
        response = browser.open(request, timeout=5).read().decode()
        filename_dir = json.loads(response)["url"]
        request = Request(url="http://{}{}".format(command_addr, filename_dir))
        request.add_header('User-Agent', get_useragent())
        response = browser.open(request, timeout=5).read().decode()
        if response == file_stored:
            return filename_dir
    except HTTPError:
        raise DownException("Service timed out!")
    except ValueError:
        raise MumbleException("Can't upload files!")
    except KeyError:
        raise MumbleException("Can't find file!")
    except UnicodeDecodeError:
        raise MumbleException("Bad blog encoding!")


def prepare_post_request(url, data):
    data = ["{}={}".format(key, quote(data[key])) for key in data]
    request = Request(url="http://{}".format(url))
    request.method = "POST"
    request.data = bytes("&".join(data), "utf-8")
    request.add_header('User-Agent', get_useragent())
    return request


def random_string(start, end):
    return "".join(random.sample(
        list(string.ascii_lowercase) * 10, random.randint(start, end)
    ))


class DownException(Exception):
    pass


class MumbleException(Exception):
    pass
