import os
import time

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException

driver = None

try:
    profile_path = os.environ['FIREFOX_PROFILE_PATH']
except KeyError:
    raise


def send_whatsapp(pdf, phone, excel=None):
    global driver

    try:
        driver.quit()
    except AttributeError:
        pass
    except:
        raise

    if excel:
        paths = (pdf, excel)
    else:
        paths = (pdf, )

    url = 'https://web.whatsapp.com/send?phone={phone}'
    profile = FirefoxProfile(profile_path)

    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver.get(url.format(phone=phone))
    driver.maximize_window()

    clip_xpath = '//div[@title="Adjuntar"]'

    try:
        clip = WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.XPATH, clip_xpath))
        )

        try:
            clip.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click()", clip)

        accept_xpath = '//input[@accept="*"]'

        for file in paths:
            image_box = WebDriverWait(driver, 20).until(
                ec.presence_of_element_located((By.XPATH, accept_xpath))
            )

            image_box.send_keys(file)

    except:
        raise

