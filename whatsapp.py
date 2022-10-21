
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import sys

from selenium.webdriver.chrome.options import Options


options = Options()
options.add_argument('-start-maximized')
options.add_argument('-disable-infobars')

options = Options()
options.add_argument(
    r'user-data-dir=C:\Users\Andrei\AppData\Local\Google\Chrome\User Data',

)

browser = webdriver.Chrome(options=options)

browser.maximize_window()

browser.switch_to('WhatsApp')


