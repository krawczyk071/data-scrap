from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os
import pages

# from config import rand_proxy


class Otodom():
    def __init__(self):
        self.options = Options()
        # self.options.add_argument("--headless=new")
        # self.options.add_argument('--proxy-server=95.216.114.142:80')
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        # PROXY
        # proxy = rand_proxy()
        # self.options.add_argument(f'--proxy-server={proxy}')
        self.driver = webdriver.Chrome(options=self.options)
        # self.driver.get("http://www.otodom.pl")
        self.is_working = False
        # check connection
        # self.is_connected()

    def is_connected(self):
        self.driver.get('http://www.90minut.pl/')
        el = self.driver.find_element(By.TAG_NAME, 'body').text
        is_bad = 'ERR_TIMED_OUT' in el
        self.is_working = not is_bad
        print('Connection failed' if is_bad else 'Connection ok')

    def tearDown(self):
        self.driver.close()


    def run(self):
        main_page = pages.MainPage(self.driver)
        main_page.start()
        main_page.click_cookie()
        main_page.scroll_load()
        main_page.get_page_info()


if __name__ == "__main__":
    page = Otodom()
    page.run()
