
import json, time
from tqdm import tqdm
import pages
from exporter import Ecsv,Etxt
from utils import Crawler,Static,Parser
import concurrent.futures
import threading
from jsonextractors import extract_oferta_from_json,extract_ads_from_json
from typing import Literal


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

    def stat_otodom_all(self,type:Literal['sell','rent'],woj:str,miasto:str,start:int=1,end:int|None=None)->str:
        def make_url(woj, miasto, page=1,type='sell'):
            if type == 'sell':
                return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'
            else:
                return f'https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'

        self.crawler = Static()

        self.fieldnames = ['id', 'title', 'slug', 'estate', 'developmentId', 'transaction', 'isPrivateOwner', 'agency', 'totalPrice', 'rentPrice', 'areaInSquareMeters', 'roomsNumber', 'peoplePerRoom', 'dateCreated', 'dateCreatedFirst', 'pushedUpAt', 'latitude', 'longitude', 'cityname', 'districtname', 'streetname', 'number', 'geo']
        self.writer = Ecsv(mode='w',fieldnames=self.fieldnames)               
        
        def worker(page,woj,miasto):
            link=make_url(woj, miasto, page, type)
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

    MODE='stat_all'
    WOJEWODZTWO='mazowieckie'
    GMINA='warszawa'
    MIASTO='warszawa'
    RODZAJ_TRANSAKCJI='rent'
    PATH_LISTA=r'main_najm_wawa_fulloutput20230814-145110.csv'
    # r'C:\Users\krawc\OneDrive\Documents\code\pythons\pandas-projects\otodom\out3.csv'
    START=0
    STOP=None

    runner = Runner()
    thread_local = threading.local()

    match MODE:
            case "dyn_all":
                runner.otodom_all(WOJEWODZTWO,MIASTO)
            case "dyn_one":
                runner.otodom_one(PATH_LISTA)
            case "stat_all":
                runner.stat_otodom_all(RODZAJ_TRANSAKCJI,WOJEWODZTWO,MIASTO)
            case "stat_one":
                runner.stat_otodom_one(PATH_LISTA,START)

# sqlite exporter
# 170 stron 1h

