import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import webbrowser

url = 'https://web.whatsapp.com/'
profile = FirefoxProfile(r'C:\Users\Andrei\AppData\Roaming\Mozilla\Firefox\Profiles\ad46gjms.default-release')
#
# firefox = webbrowser.Mozilla(r'C:\Program Files\Mozilla Firefox\firefox.exe')
# firefox.open(url)

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver = webdriver.Firefox(firefox_profile=profile, options=options)
driver.get(url)
time.sleep(13)

xpath = "//span[@title='Laura']"


user = driver.find_element_by_xpath(xpath)

user.click()

