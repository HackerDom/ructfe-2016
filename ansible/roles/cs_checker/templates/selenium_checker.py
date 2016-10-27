#!/usr/bin/env python3

import sys
import signal
import random
from selenium import webdriver, common

OK, GET_ERROR, CORRUPT, FAIL, INTERNAL_ERROR = 101, 102, 103, 104, 110


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


def make_driver(to_url):
    return webdriver.PhantomJS(service_log_path='/tmp/phant-' + to_url + '.log',
                               service_args=['--webdriver-loglevel=DEBUG',
                                             '--debug=true',
                                             '--local-url-access=false'])


def init_check(address):

    # ignore command id's
    with open("sites.txt") as sites_file:
        sites = [site.strip() for site in sites_file.readlines()]
    address = sites[random.randint(0, len(sites))]

    driver = None
    while True:
        try:
            driver = make_driver(address)
            break
        except Exception:
            driver.service.process.send_signal(signal.SIGTERM)
            driver.quit()
            driver = None

    driver.set_page_load_timeout(15)

    try:
        driver.get("http://{}".format(address))
        driver.save_screenshot('/tmp/phant-' + address + '.png')
    except common.exceptions.TimeoutException:
        close(
            FAIL,
            "Failed to put the flag due to {} timed out".format(address),
            "Failed to put the flag due to {} timed out".format(address)
              )
    except Exception as e:
        close(
            FAIL,
            "Failed to put the flag due to {}".format(e),
            "Failed to put the flag due to {}".format(e)
              )
    finally:
        driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()


def check(addr):
    init_check(addr)
    close(OK)


def put(addr, flag_id, flag, vuln=None):
    init_check(addr)
    close(OK, flag_id)


def get(addr, checker_flag_id, flag, vuln=None):
    init_check(addr)
    close(OK)


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {
    'check': check,
    'put': put,
    'get': get,
    'info': info
}


def not_found(*args):
    close(
        INTERNAL_ERROR,
        "Checker error",
        "Unsupported command %s" % sys.argv[1]
    )


if __name__ == '__main__':
    try:
        COMMANDS.get(sys.argv[1], not_found)(*sys.argv[2:])
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except OSError as e:
        close(CORRUPT, "Socket I/O error", "SOCKET ERROR: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "INTERNAL ERROR: %s" % e)
