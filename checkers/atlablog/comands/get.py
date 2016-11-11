from comands.phantom_js import get_driver, DriverInitializationException, DriverTimeoutException
from comands import OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR
from templates.selenium_forms import parse_authorization_form
import traceback
from selenium.webdriver import PhantomJS
from selenium.common.exceptions import NoSuchElementException

from comands import OK, MUMBLE, DOWN
from templates.urllib_forms import MumbleException, DownException, prepare_post_request

from urllib.request import build_opener, HTTPCookieProcessor, HTTPRedirectHandler
import re


def non_selenium_get(command_ip, flag_id, flag, vuln):
    username, password, post_id = flag_id.split(":")
    browser = build_opener(
        HTTPCookieProcessor,
        HTTPRedirectHandler
    )
    try:
        data = {
            "username": username,
            "password": password
        }

        request = prepare_post_request("{}/login".format(command_ip), data)
        response = browser.open(request).read().decode()
        print(browser)
        if flag.lower() in response:
            return {
                "code": OK
            }
        return {
            "code": CORRUPT,
            "public": "Can't find my post!"
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


def init_get(command_ip, flag_id, flag, vuln):
    try:
        user, password, post_id = flag_id.split(":")
        with get_driver() as driver:
            run_get_logic(driver, command_ip, user, password, post_id, flag)
    except DriverInitializationException as e:
        return {
            "code": CHECKER_ERROR,
            "private": "Couldn't init driver due to {} with {}".format(
                e, traceback.format_exc()
            )
        }
    except DriverTimeoutException as e:
        return {
            "code": MUMBLE,
            "public": "Service response timed out!",
            "private": "Service response timed out due to {}".format(e)
        }
    except Exception as e:
        return {
            "code": CHECKER_ERROR,
            "private": "ATTENTION!!! Unhandled error: {}".format(e)
        }


def run_get_logic(driver: PhantomJS, comand_id, username, password, post, flag):
    cookies = parse_authorization_form(driver, comand_id, username, password)
    if not cookies:
        return {
            "code": MUMBLE,
            "public": "Can't authorize!"
        }
    driver.get("http://{}/{}".format(comand_id, post))
    try:
        flag_there = driver.find_element_by_xpath('//li/a[@href="#"]')
        flag_container = flag_there.text
        if flag.lower() in flag_container:
            return {
                "code": OK
            }
        return {
            "code": CORRUPT,
            "public": "Can't find my post!"
        }
    except NoSuchElementException:
        return {
            "code": CORRUPT,
            "public": "Can't find my post!"
        }