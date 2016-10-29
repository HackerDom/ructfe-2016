#!/usr/bin/env python3

import sys
import signal
import json
import os
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


def ip_to_id(ip):
    ips_file = "command_logs.json"
    if not os.path.exists(ips_file):
        with open(ips_file, 'w') as dump_file:
            dump_file.write("{}")

    with open(ips_file, mode="r") as dump_file:
        ips_dict = json.load(dump_file)
        if ip in ips_dict:
            return ips_dict[ip]
        else:
            ips_dict[ip] = len(ips_dict)

    with open(ips_file, mode="w") as dump_file:
        json.dump(ips_dict, dump_file)
        return ips_dict[ip]


def init_check(command_ip):
    with open("sites.txt") as sites_file:
        sites = [site.strip() for site in sites_file.readlines()]
    address = sites[ip_to_id(command_ip) % len(sites)]

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


def check(command_ip):
    init_check(command_ip)
    close(OK)


def put(command_ip, flag_id, flag, vuln=None):
    init_check(command_ip)
    close(OK, flag_id)


def get(command_ip, checker_flag_id, flag, vuln=None):
    init_check(command_ip)
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
        close(CORRUPT, "Service did not work as expected",
              "Checker exception: %s" % e)
    except OSError as e:
        close(CORRUPT, "Socket I/O error", "SOCKET ERROR: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "INTERNAL ERROR: %s" % e)