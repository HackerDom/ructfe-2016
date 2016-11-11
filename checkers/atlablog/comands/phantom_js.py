from selenium import webdriver, common
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from contextlib import contextmanager
from templates.user_agents import get as get_header
import signal


def __init_phantom_js_driver():

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (get_header(),)
    current_date = datetime.isoformat(datetime.now())
    return webdriver.PhantomJS(service_log_path='/tmp/phant-' + current_date + '.log',
                               service_args=['--webdriver-loglevel=DEBUG',
                                             '--debug=true',
                                             '--local-url-access=false'],
                               desired_capabilities=dcap
                               )


@contextmanager
def get_driver(timeout=15):
    try:
        driver = __init_phantom_js_driver()
    except Exception:
        try:
            driver = __init_phantom_js_driver()
        except Exception as e:
            raise DriverInitializationException(
                "Failed to init driver due to {}".format(e)
            )

    driver.set_page_load_timeout(timeout)
    try:
        yield driver
    except common.exceptions.TimeoutException:
        raise DriverTimeoutException(
            "Failed to handle driver, due to page loading timed out!"
        )
    finally:
        driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()


class DriverTimeoutException(Exception):
    """Handles Timeout errors"""
    def __init__(self, msg):
        super(DriverTimeoutException, self).__init__(msg)


class DriverInitializationException(Exception):
    """Handles on-init errors"""
    def __init__(self, msg):
        super(DriverInitializationException, self).__init__(msg)
