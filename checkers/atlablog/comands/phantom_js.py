from selenium import webdriver, common
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from contextlib import contextmanager
from templates.user_agents import get
import signal


def __init_phantom_js_driver():

    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (str(get()))
    current_date = datetime.isoformat(datetime.now())
    driver = webdriver.PhantomJS(
        desired_capabilities=dcap,
        service_log_path='/tmp/phant-' + current_date + '.log',
        service_args=
            [
                '--debug=true',
                '--webdriver-loglevel=DEBUG',
                '--local-url-access=false'
            ]
    )
    return driver

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
