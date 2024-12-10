import logging

import geckodriver_autoinstaller
from django.shortcuts import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# Install Firefox Webdriver
geckodriver_autoinstaller.install()

# Suppress Selenium warnings
logging.getLogger("selenium").setLevel(logging.CRITICAL)
logging.getLogger("django.request").setLevel(logging.CRITICAL)

"""Package initialiser to ensure all Selenium tests have access to these common functions"""


def log_in_via_form(driver: WebDriver, live_server_url: str, username: str, password: str):
    """
    Automates the login process for a user in Selenium.

    :param username: The username to log in with.
    :param password: The password to log in with.:
    :param live_server_url: The URL of the live server.
    :param driver: The selenium webdriver instance.
    """
    driver.get(f"{live_server_url}{reverse('log_in')}")
    wait(driver)

    username_input = driver.find_element(By.ID, "id_username")
    password_input = driver.find_element(By.ID, "id_password")
    login_button = driver.find_element(By.ID, "id_submit_log_in_page")
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    wait(driver)


def logout(driver: WebDriver, live_server_url: str):
    driver.get(f"{live_server_url}{reverse('log_out')}")


def wait(driver_client):
    WebDriverWait(driver_client, 10).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )


def wait_for_element(driver_client, by, value, timeout=10):
    return WebDriverWait(driver_client, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_for_clickable(driver_client, elem: WebElement, timeout=10):
    return WebDriverWait(driver_client, timeout).until(
        EC.element_to_be_clickable(elem)
    )
