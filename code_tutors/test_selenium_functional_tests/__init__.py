from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


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
