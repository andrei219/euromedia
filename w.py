from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.add_argument(r'-user-data-dir=C:\Users\Andrei\AppData\Roaming\Mozilla\Firefox\Profiles')

driver = webdriver.Firefox(options=options)

driver.get("https://web.whatsapp.com/")


print(driver.get_cookies())