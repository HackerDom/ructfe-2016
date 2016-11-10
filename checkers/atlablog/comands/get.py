from comands.phantom_js import get_driver, DriverInitializationException, DriverTimeoutException
from comands import OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR
import traceback


def init_get(command_ip, flag_id, flag, vuln):
    try:
        with get_driver() as driver:
            driver.get("http://{}".format(command_ip))
            run_get_logic(driver)
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


def run_get_logic(driver):
    #TODO Try to register random user
    #TODO Try to post comments
    return {
        "code": OK
    }