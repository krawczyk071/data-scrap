from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import pages
from exporter import Ecsv
from utils import Proxy

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
        # proxy = Proxy.rand_proxy()
        # self.options.add_argument(f'--proxy-server={proxy}')
        self.driver = webdriver.Chrome(options=self.options)
        # self.driver.get("http://www.otodom.pl")
        self.is_working = False
        self.is_reseted = False
        self.crawl_cnt = 0
        # check connection
        # self.is_connected()
        self.page_last = 1
        self.page_range = range(2, self.page_last+1)
        
        
    def reconnect(self):
        if self.crawl_cnt> 20:
            self.is_working = False

        while (not self.is_working):
            # try to make connection
            proxy = Proxy.rand_proxy()
            self.options.add_argument(f'--proxy-server={proxy}')
            self.driver = webdriver.Chrome(options=self.options)
            # verify
            self.is_connected()
            self.is_reseted = True
            self.crawl_cnt = 0

    def is_connected(self):
        self.driver.get('http://www.90minut.pl/')
        el = self.driver.find_element(By.TAG_NAME, 'body').text
        is_bad = 'ERR_TIMED_OUT' in el
        self.is_working = not is_bad
        if is_bad:
            self.driver = None
            print('Connection failed' )
            self.reconnect()
        else:
            print('Connection ok')

    def tearDown(self):
        self.driver.close()

    def update_last(self,newval):
        self.page_last = newval
        self.page_range = range(2, self.page_last+1)

    def run_main(self):
        self.fieldnames = ['date', 'link', 'name', 'where','price', 'perm', 'rooms', 'sqm', 'who']
        self.writer = Ecsv(self.fieldnames)
        # first
        main_page = pages.MainPage(self.driver,self.writer,1,update_last=self.update_last)
        main_page.start()
        main_page.click_cookie()
        main_page.scroll_load()
        main_page.get_page_info()
        main_page.get_html()
        main_page.parse()
        # others
        if self.page_last>1:
            for page in self.page_range:
                main_page = pages.MainPage(self.driver,self.writer,page)
                main_page.start()
                main_page.scroll_load()
                main_page.get_html()
                main_page.parse()

    def run_detail(self):

        self.fieldnames = ['link', 'Nr oferty w biurze ', 'date', 'imgs', 'tel', 'Piętro', 'Czynsz', 'Okna', 'Typ ogłoszeniodawcy', 'Rynek', 'Ogrzewanie',
                  'Materiał budynku', 'Rodzaj zabudowy', 'author', 'Miejsce parkingowe', 'Rok budowy', 'Stan wykończenia', 'Liczba pokoi', 'Dostępne od', 'Winda', 'Wyposażenie', 'Zabezpieczenia', 'Media', 'Balkon / ogród / taras', 'Informacje dodatkowe', 'Forma własności', 'full', 'Obsługa zdalna', 'Powierzchnia', 'Nr oferty w Otodom', 'Data dodania', 'Data aktualizacji']
        self.writer = Ecsv(self.fieldnames)
    
        links = ['https://www.otodom.pl/pl/oferta/mieszkanie-22-50-m-lodz-ID4iIbp',
             'https://www.otodom.pl/pl/oferta/mieszkanie-m3-lanowa-37m2-teofilow-bezposrednio-ID4ll0F',
             'https://www.otodom.pl/pl/oferta/apartamenty-zolnierska-12-aa-2-ID4lVwG']
        
        for link in links:
            det_page = pages.DetailPage(self.driver,self.writer,link=link)
            det_page.start()
            det_page.click_cookie()
            det_page.scroll_load()
            det_page.telshow()
            det_page.modal()
            det_page.details()
            det_page.get_html()
            det_page.parse()

            self.crawl_cnt += 1
            # self.reconnect()

if __name__ == "__main__":
    page = Otodom()
    page.run_detail()

# crawler
# parser
# dumper