from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json, time
from tqdm import tqdm
import pages
import proxyjson
from exporter import Ecsv,Etxt
from utils import Proxy,Static,Parser
import concurrent.futures
import threading
from jsonextractors import extract_oferta_from_json,extract_ads_from_json

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

    def stat_otodom_one(self,ipt_path:str,start:int|None=None,end:int|None=None)->str:
        self.crawler = Static()

        self.fieldnames = ['id', 'publicId', 'advertType', 'createdAt', 'modifiedAt', 'description', 'exclusiveOffer', 'externalId', 'features', 'title', 'agency', 'adCategoryname', 'adCategorytype', 'latitude', 'longitude', 'cityname', 'districtname', 'streetname', 'number', 'rent', 'costs', 'condition', 'ownership', 'ownername', 'phones', 'images', 'Area', 'Building_floors_num', 'Building_type', 'Building_material', 'Build_year', 'Construction_status', 'Extras_types', 'Floor_no', 'Heating', 'MarketType', 'OfferType', 'Price', 'ProperType', 'Rooms_num', 'Windows_type', 'Lift', 'voivodeship', 'city_or_village', 'district', 'residential','commune', 'county','Deposit', 'Equipment_types']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)
        # self.writer = Etxt(mode='w')
        self.err_writer = Ecsv(mode='w',fieldnames=['inactive'],filename='./output_err.csv')
        
        self.input = Ecsv(mode='r',filename=ipt_path)
        # links = [row['link'] for row in self.input.rows][start:end]
        links = ['https://www.otodom.pl/pl/oferta/'+row['slug'] for row in self.input.rows][start:end]
        # timestr = time.strftime("%Y%m%d-%H%M%S")

        for link in tqdm(links):
            html = self.crawler.get_html(link)
            soup = Parser(html)

            page_json=soup.select_one('#__NEXT_DATA__').text            
            json_data=json.loads(page_json)
            extr = extract_oferta_from_json(json_data)

            if extr['is_oferta']:
                self.writer.save_row(extr['data'])
            else:
                self.err_writer.save_row({'inactive':link[-7:]})
            
            # print(extr['info']['userSessionId'])
            if extr['info']['isBotDetected']:
                print('BOT detected')

    def stat_otodom_all(self,type:str,woj:str,miasto:str,start:int=1,end:int|None=None)->str:
        def make_url(woj, miasto, page=1,type='sell'):
            if type == 'sell':
                return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'
            else:
                return f'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'

        self.crawler = Static()

        self.fieldnames = ['id', 'title', 'slug', 'estate', 'developmentId', 'transaction', 'isPrivateOwner', 'agency', 'totalPrice', 'rentPrice', 'areaInSquareMeters', 'roomsNumber', 'peoplePerRoom', 'dateCreated', 'dateCreatedFirst', 'pushedUpAt', 'latitude', 'longitude', 'cityname', 'districtname', 'streetname', 'number', 'geo']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)               
        
        def worker(page,woj,miasto):
            link=make_url(woj, miasto, page,type)
            html = self.crawler.get_html(link)
            soup = Parser(html)

            page_json=soup.select_one('#__NEXT_DATA__').text            
            json_data=json.loads(page_json)
            extr = extract_ads_from_json(json_data)
            self.writer.save_rows(extr['data_list'])
            if page == start:
                self.pagination = extr['pagination']
                self.page_range = range(self.pagination['page'], min(self.pagination['totalPages']+1,end+1) if end else self.pagination['totalPages']+1)
                print(f'total pages: {self.pagination["totalPages"]}')
                        
            # print(extr['info']['userSessionId'])
            if extr['info']['isBotDetected']:
                print('BOT detected')
        # start
        worker(start,woj,miasto)        
        # others
        if len(self.page_range)>1:
            for page in tqdm(self.page_range[1:]):
                worker(page,woj,miasto)


if __name__ == "__main__":
    thread_local = threading.local()
    runner = Runner()
    # runner.otodom_all('mazowieckie','warszawa')
    # runner.otodom_one('./input2.csv')
    # runner.stat_otodom_one(r'C:\Users\krawc\OneDrive\Documents\code\pythons\pandas-projects\otodom\out3.csv',1273+2616+1015+6080)
    runner.stat_otodom_one(r'main_najm_wawa_fulloutput20230814-145110.csv')
    # runner.stat_otodom_all('rent','mazowieckie','warszawa')


# crawler
# parser
# dumper

# mutithread concurrent.futures / asyncio 
# resume
# sqlite exporter

    # 170 stron 1h

