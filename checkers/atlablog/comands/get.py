from comands.phantom_js import get_driver, DriverInitializationException, DriverTimeoutException

import traceback
from selenium.webdriver import PhantomJS
from selenium.common.exceptions import NoSuchElementException

from comands import OK, MUMBLE, DOWN, CHECKER_ERROR, CORRUPT
from templates.urllib_forms import MumbleException, DownException, prepare_post_request

from urllib.request import build_opener, HTTPCookieProcessor, HTTPRedirectHandler
from http.cookiejar import LWPCookieJar


def non_selenium_get(command_ip, flag_id, flag, vuln):
    username, password, post_id = flag_id.split(":")
    cookies = LWPCookieJar()
    browser = build_opener(
        HTTPCookieProcessor(cookies),
        HTTPRedirectHandler
    )
    try:
        data = {
            "username": username,
            "password": password
        }

        request = prepare_post_request("{}/login".format(command_ip), data)
        response = browser.open(request).read().decode()
        session = {}
        for cookie in cookies:
            session[cookie.name] = cookie.value
        return session

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
            cookies = non_selenium_get(command_ip, flag_id, flag, vuln)
            return run_get_logic(driver, command_ip, post_id, flag, cookies)
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


def run_get_logic(driver: PhantomJS, comand_id, post, flag, cookies):
    driver.add_cookie({
        'name': 'sessions',
        'value': cookies['sessions'],
        'domain': "." + comand_id.split(":")[0],
        'path': '/'
    })
    driver.get("http://{}/{}".format(comand_id, post))
    try:
        flag_there = driver.find_element_by_xpath('//li/a[@href="#"]')
        flag_container = flag_there.get_attribute('innerHTML')
        if flag in flag_container:
            return {
                "code": OK
            }
        else:
            return {
                "code": CORRUPT,
                "public": "Can't find my private data!"
            }
    except NoSuchElementException:
        return {
            "code": CORRUPT,
            "public": "Can't find my private data!"
        }
