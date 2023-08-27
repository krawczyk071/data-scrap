import requests, json
import random
from random import randint
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from exporter import Ecsv
import proxyjson

class Parser(BeautifulSoup):
    def __init__(self,html,parser="html.parser"):
        super().__init__(html,parser)
    # soup = BeautifulSoup(self.html, "html.parser")
    # organic = soup.select_one(MainPageLocators.organic)
    # itms = organic.select(MainPageLocators.itms)

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

    # def run_main(self,skip=-1):
    #     self.fieldnames = ['date', 'link', 'name', 'where','price', 'perm', 'rooms', 'sqm', 'who']
    #     self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)

    #     def worker(page,woj,miasto):
    #         main_page = pages.MainPage(self.driver,self.writer,page=page,update_last=self.update_last if page==1 else None)
    #         main_page.start(woj,miasto)
    #         if self.crawl_cnt==0:
    #             main_page.click_cookie()
    #         main_page.scroll_load()
    #         if page==1:
    #             main_page.get_page_info()
    #             self.update_last(3)
    #         main_page.get_html()
    #         main_page.parse()
    #         print(page)
    #         self.crawl_cnt += 1
    #         self.reconnect()

    #     # first
    #     worker(1,'lodzkie','lodz')

    #     # others
    #     for page in tqdm(self.page_range):
    #         try:
    #             if page <= skip:
    #                 continue
    #             worker(page,'lodzkie','lodz')
    #         except:
    #             writer = Ecsv(mode='w',fieldnames=['failed'])
    #             writer.save_row({'failed':page})
    #             raise


    # def run_detail(self):

    #     self.fieldnames = ['link', 'Nr oferty w biurze ', 'date', 'imgs', 'tel', 'Piętro', 'Czynsz', 'Okna', 'Typ ogłoszeniodawcy', 'Rynek', 'Ogrzewanie',
    #               'Materiał budynku', 'Rodzaj zabudowy', 'author', 'Miejsce parkingowe', 'Rok budowy', 'Stan wykończenia', 'Liczba pokoi', 'Dostępne od', 'Winda', 'Wyposażenie', 'Zabezpieczenia', 'Media', 'Balkon / ogród / taras', 'Informacje dodatkowe', 'Forma własności', 'full', 'Obsługa zdalna', 'Powierzchnia', 'Nr oferty w Otodom', 'Data dodania', 'Data aktualizacji']
    #     self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)
    #     self.input = Ecsv(mode='r',filename='./input2.csv')
    #     links = ['https://www.otodom.pl'+ row['link'] for row in self.input.rows][:20]
           
    #     for link in links:
    #         det_page = pages.DetailPage(self.driver,self.writer,link=link)
    #         det_page.start()
    #         det_page.click_cookie()
    #         det_page.scroll_load()
    #         if det_page.check_active():
    #             det_page.telshow()
    #             det_page.details()
    #             det_page.get_html()
    #             det_page.parse()
    #         else:
    #             print('inactive',link)

    #         self.crawl_cnt += 1
    #         self.reconnect()

class Proxy():
    def __init__(self):
        self.current = None
        self.load_list()
        self.warn_list = []

    def load_list(self):
        reader = Ecsv(mode='r',filename='./proxylist.csv')
        self.ips = [row['proxy'] for row in reader.rows]

    def rotate_proxy(self):
        if len(self.ips)<2:
            print('List too short')

        proxy = random.choice(self.ips)
        while proxy==self.current:
            proxy = random.choice(self.ips)
        self.current = proxy  
        return proxy
    
    def blacklist(self,ip):        
        if ip in self.warn_list[-2:]:
            self.ips.remove(ip)
            print(f'proxy {ip} removed from rotation' )
        else:
            self.warn_list.append(ip)
            print(f'WARNING for {ip}')

class Static():
    def __init__(self,use_proxy=True):
        self.headers= {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'Accept-Encoding': 'gzip',
                        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
                        'Upgrade-Insecure-Requests': '1',
                        'Referer': 'https://www.google.com/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        # self.params={'q': 'requests+language:python'},

        self.use_proxy = use_proxy
        self.proxy_blacklisted = []
        # PROXY
        self.proxy = Proxy()
        self.set_proxy()

    def check_proxy(self):
        res = requests.get(url='http://httpbin.org/ip',headers=self.headers,proxies=self.proxies)
        el = res.text
        try:
            res = json.loads(el)
            if ('origin' in res) & (res['origin']==self.proxy_ip.split(':')[0]):
                print('verified origin',res['origin'])
                return True
        except:
            return False

    def set_proxy(self):
        if self.use_proxy:
            self.proxy_ip = self.proxy.rotate_proxy()
            # proxy with login
            ip,port,user,pwd = self.proxy_ip.split(':')
            self.proxies = {'http': f'http://{user}:{pwd}@{ip}:{port}/'}
        else:
            self.proxies = None

    def get_html(self,url,delay=True):
        self.status_code = None
        # random delay
        if delay:
            random_delay = randint(2,8)
            sleep(random_delay)

        while self.status_code!=200:
            self.response = requests.get(url=url,headers=self.headers,proxies=self.proxies)
            self.status_code = self.response.status_code
            # print(self.status_code)
            if self.status_code != 200:
                print(f'Connection failed {self.status_code}')
                self.proxy.blacklist(self.proxy_ip)
            self.set_proxy()

        return self.response.text


