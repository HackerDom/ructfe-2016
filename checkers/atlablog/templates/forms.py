from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotSelectableException



def parse_authorization_form(driver: webdriver.PhantomJS, ip, username, password):
    driver.get("http://{}/login".format(ip))
    try:
        username_form = driver.find_element_by_id("username")
        password_form = driver.find_element_by_id("password")
        submit_button = driver.find_element_by_xpath('//form/button[@type="submit"]')
    except NoSuchElementException:
        return None
    try:
        username_form.send_keys(username)
        password_form.send_keys(password)
        submit_button.click()
    except ElementNotSelectableException:
        return None

    return driver.get_cookies()


def make_post(driver: webdriver.PhantomJS, ip, title, text):
    driver.get("http://{}".format(ip))
    try:
        title_form = driver.find_element_by_id("title")
        text_form = driver.find_element_by_id("js-file-upload-area")
        submit_button = driver.find_element_by_xpath('//form/button[@type="submit"]')
    except NoSuchElementException as e:
        print(e)
        return None
    try:
        title_form.send_keys(title)
        text_form.send_keys(text)
        submit_button.click()
    except ElementNotSelectableException:
        return None
    try:
        link = driver.find_element_by_link_text(title)
        return "http://{}/{}".format(ip, link.text)
    except NoSuchElementException as e:
        print(e)
        return None
