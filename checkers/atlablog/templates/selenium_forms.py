from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotSelectableException


def parse_authorization_form(driver: webdriver.PhantomJS, ip, username, password):
    driver.get("http://{}/login".format(ip))
    try:
        username_form = driver.find_element_by_id("username")
        password_form = driver.find_element_by_id("password")
        submit_button = driver.find_element_by_xpath('//form/button[@type="submit"]')

        username_form.send_keys(username)
        password_form.send_keys(password)
        submit_button.click()
    except NoSuchElementException:
        return None
    except ElementNotSelectableException:
        return None
    return driver.get_cookies()