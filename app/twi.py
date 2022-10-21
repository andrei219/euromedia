import os.path
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


from selenium.webdriver.chrome.options import Options


# options = Options()
# options.add_argument('--start-maximized')
# options.add_argument('--disable-infobars')

options = Options()
options.add_argument(
    r'user-data-dir=C:\Users\Andrei\AppData\Local\Google\Chrome\User Data',

)

options.add_experimental_option('detach', True)
try:
    driver = webdriver.Chrome(options=options)
except:
    pass
try:
    driver.get('https://web.whatsapp.com/')
except:
    pass

