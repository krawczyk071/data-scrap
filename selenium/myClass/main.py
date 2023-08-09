from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
from tqdm import tqdm
import pages
import proxyjson
from exporter import Ecsv
from utils import Proxy
import concurrent.futures
import threading


class Crawler():
    def __init__(self,headless=False,no_images=True,crawl_limit=20,use_proxy=True):
        self.options = Options()
        self.options.add_argument("start-maximized")
        self.options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        # Headless
        if headless:
            self.options.add_argument("--headless=new")
        # Disable Image Loading
        if no_images:
            self.options.add_argument('--blink-settings=imagesEnabled=false')

        self.use_proxy = use_proxy
        self.is_working = False
        self.crawl_cnt = 0
        self.crawl_limit = crawl_limit

        # PROXY
        self.proxy = Proxy()
        # check connection
        self.reconnect()
        
    def is_connected(self):
        self.driver.get('https://httpbin.org/ip')
        el = self.driver.find_element(By.TAG_NAME, 'body').text
        try:
            res = json.loads(el)
            if 'origin' in res:
                self.is_working = True
                print('verified origin',res['origin'])
        except:
            self.is_working = False

        if self.use_proxy:
            if not self.is_working:
                self.driver = None
                print('Connection failed' )
                self.proxy.blacklist(self.proxy_ip)
                print(f'proxy {self.proxy_ip} removed from rotation' )
                self.reconnect()
            else:
                print('Connection OK', self.proxy_ip)
                self.crawl_cnt = 0
        else:
            if not self.is_working:
                self.driver = None
                print('Connection failed' )                
            else:
                print('Connection OK - NO PROXY')

        
    def reconnect(self):
        if self.use_proxy:
            if self.crawl_cnt > self.crawl_limit:
                self.is_working = False

            while (not self.is_working):
                # try to make connection
                self.proxy_ip = self.proxy.rotate_proxy()
                # proxy withot login
                # self.options.add_argument(f'--proxy-server={self.proxy_ip}')
                # proxy with login
                proxyjson.add_proxyjson_to_options(self.options,self.proxy_ip)

                # get new DRIVER
                self.driver = webdriver.Chrome(options=self.options)
                # verify
                self.is_connected()
        else:
            # get new DRIVER
            self.driver = webdriver.Chrome(options=self.options)
            # verify
            self.is_connected()

    def tearDown(self):
        self.driver.close()

    def run_main(self,skip=-1):
        self.fieldnames = ['date', 'link', 'name', 'where','price', 'perm', 'rooms', 'sqm', 'who']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)

        def worker(page,woj,miasto):
            main_page = pages.MainPage(self.driver,self.writer,page=page,update_last=self.update_last if page==1 else None)
            main_page.start(woj,miasto)
            if self.crawl_cnt==0:
                main_page.click_cookie()
            main_page.scroll_load()
            if page==1:
                main_page.get_page_info()
                self.update_last(3)
            main_page.get_html()
            main_page.parse()
            print(page)
            self.crawl_cnt += 1
            self.reconnect()

        # first
        worker(1,'lodzkie','lodz')

        # others
        for page in tqdm(self.page_range):
            try:
                if page <= skip:
                    continue
                worker(page,'lodzkie','lodz')
            except:
                writer = Ecsv(mode='w',fieldnames=['failed'])
                writer.save_row({'failed':page})
                raise


    def run_detail(self):

        self.fieldnames = ['link', 'Nr oferty w biurze ', 'date', 'imgs', 'tel', 'Piętro', 'Czynsz', 'Okna', 'Typ ogłoszeniodawcy', 'Rynek', 'Ogrzewanie',
                  'Materiał budynku', 'Rodzaj zabudowy', 'author', 'Miejsce parkingowe', 'Rok budowy', 'Stan wykończenia', 'Liczba pokoi', 'Dostępne od', 'Winda', 'Wyposażenie', 'Zabezpieczenia', 'Media', 'Balkon / ogród / taras', 'Informacje dodatkowe', 'Forma własności', 'full', 'Obsługa zdalna', 'Powierzchnia', 'Nr oferty w Otodom', 'Data dodania', 'Data aktualizacji']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)
        self.input = Ecsv(mode='r',filename='./input2.csv')
        links = ['https://www.otodom.pl'+ row['link'] for row in self.input.rows][:20]
           
        for link in links:
            det_page = pages.DetailPage(self.driver,self.writer,link=link)
            det_page.start()
            det_page.click_cookie()
            det_page.scroll_load()
            if det_page.check_active():
                det_page.telshow()
                det_page.details()
                det_page.get_html()
                det_page.parse()
            else:
                print('inactive',link)

            self.crawl_cnt += 1
            self.reconnect()

class Runner():
    def __init__(self,max_workers=2):        
        self.max_workers = max_workers
        self.page_last = 1
        self.page_range = range(2, self.page_last+1)

    def update_last(self,newval):
        self.page_last = newval
        self.page_range = range(2, self.page_last+1)

    def get_browser(self):
        if not hasattr(thread_local, "browser"):
            thread_local.browser = Crawler()
        return thread_local.browser
    
    def otodom_all(self,woj,miasto,skip=-1):
        self.fieldnames = ['date', 'link', 'name', 'where','price', 'perm', 'rooms', 'sqm', 'who']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)

        def worker(page,woj,miasto):
            browser = self.get_browser()  
            main_page = pages.MainPage(browser.driver,self.writer,page=page,update_last=self.update_last if page==1 else None)
            main_page.start(woj,miasto)
            if browser.crawl_cnt==0:
                main_page.click_cookie()
            main_page.scroll_load()
            if page==1:
                main_page.get_page_info()
                print(self.page_last)
                # self.update_last(5)
            main_page.get_html()
            main_page.parse()
            print(page)
            browser.crawl_cnt += 1
            browser.reconnect()
            if page==1:
                browser.tearDown()
                
        # first
        worker(1,woj,miasto)
        # others
        if self.page_last>1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                executor.map(lambda x: worker(x,woj,miasto), self.page_range)

    def otodom_one(self,ipt_path,start=None,end=None):

        self.fieldnames = ['link', 'Nr oferty w biurze ', 'date', 'imgs', 'tel', 'Piętro', 'Czynsz', 'Okna', 'Typ ogłoszeniodawcy', 'Rynek', 'Ogrzewanie',
                  'Materiał budynku', 'Rodzaj zabudowy', 'author', 'Miejsce parkingowe', 'Rok budowy', 'Stan wykończenia', 'Liczba pokoi', 'Dostępne od', 'Winda', 'Wyposażenie', 'Zabezpieczenia', 'Media', 'Balkon / ogród / taras', 'Informacje dodatkowe', 'Forma własności', 'full', 'Obsługa zdalna', 'Powierzchnia', 'Nr oferty w Otodom', 'Data dodania', 'Data aktualizacji']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)
        self.err_writer = Ecsv(mode='w',fieldnames=['inactive'],filename='./output_err.csv')
        
        self.input = Ecsv(mode='r',filename=ipt_path)
        links = ['https://www.otodom.pl'+ row['link'] for row in self.input.rows][start:end]

        def worker(link):   
            browser = self.get_browser() 
            det_page = pages.DetailPage(browser.driver,self.writer,link=link)
            det_page.start()
            if browser.crawl_cnt==0:
                det_page.click_cookie()
            det_page.scroll_load()
            if det_page.check_active():
                det_page.telshow()
                det_page.details()
                det_page.get_html()
                det_page.parse()
            else:
                self.err_writer.save_row({'inactive':link})
                print('inactive',link)

            self.crawl_cnt += 1
            self.reconnect()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(worker, links)

if __name__ == "__main__":
    thread_local = threading.local()
    runner = Runner()
    # runner.otodom_all('mazowieckie','warszawa')
    runner.otodom_one('./input2.csv')


# crawler
# parser
# dumper

# mutithread concurrent.futures / asyncio 
# resume
# sqlite exporter

    # 170 stron 1h