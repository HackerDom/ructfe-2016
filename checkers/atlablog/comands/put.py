from comands import OK, MUMBLE, DOWN
from templates.urllib_forms import\
    try_register_user, MumbleException, DownException, try_make_post

from urllib.request import\
    build_opener, HTTPCookieProcessor, HTTPRedirectHandler
import re


def non_selenium_put(command_ip, flag_id, flag, vuln):
    browser = build_opener(
        HTTPCookieProcessor,
        HTTPRedirectHandler
    )
    try:
        username, password, email, response = try_register_user(
            browser, command_ip, flag
        )
        title, response = try_make_post(browser, command_ip)

        links = re.findall(r'(?<=href=\").*(?=\"><h2>)', response)
        for link in links:
            if "/" + title in link.split("-")[0]:
                return {
                    "code": OK,
                    "flag_id": "{}:{}:{}".format(
                        username, password, title + "-" + link.split("-")[1]
                    )
                }

        return {
            "code": MUMBLE,
            "public": "Can't find checksystem post!"
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