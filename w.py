import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import win32gui
import win32con


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


FILEPATH = r'C:\Users\Andrei\Desktop\learning.xlsx'

url = 'https://web.whatsapp.com/send?phone={phone}'
profile = FirefoxProfile(r'C:\Users\Andrei\AppData\Roaming\Mozilla\Firefox\Profiles\ad46gjms.default-release')
#
# firefox = webbrowser.Mozilla(r'C:\Program Files\Mozilla Firefox\firefox.exe')
# firefox.open(url)



options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
driver = webdriver.Firefox(firefox_profile=profile, options=options)
driver.get(url.format(phone='+34673567274'))

clip_xpath = '//div[@title="Adjuntar"]'
attach_document_xpath = '//span[@data-testid="attach-document"]'

try:
    clip = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, clip_xpath))
    )

    clip.click()

    document_attach = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, attach_document_xpath))
    )

    document_attach.click()

    time.sleep(1)



except:
    raise

