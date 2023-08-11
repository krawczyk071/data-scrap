from bs4 import BeautifulSoup
import random
from exporter import Ecsv
import requests, json


class Parser(BeautifulSoup):
    pass
    # soup = BeautifulSoup(self.html, "html.parser")
    # organic = soup.select_one(MainPageLocators.organic)
    # itms = organic.select(MainPageLocators.itms)

class Crawler():
    pass

class Proxy():
    def __init__(self):
        self.current = None
        self.load_list()

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
        self.ips.remove(ip)

class Static():
    def __init__(self,crawl_limit=20,use_proxy=True):
        self.headers= {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'Accept-Encoding': 'gzip',
                        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
                        'Upgrade-Insecure-Requests': '1',
                        'Referer': 'https://www.google.com/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        # self.params={'q': 'requests+language:python'},

        self.use_proxy = use_proxy
        self.is_working = False
        self.crawl_cnt = 0
        self.crawl_limit = crawl_limit

        # PROXY
        self.proxy = Proxy()
        # check connection
        self.reconnect()

    def is_connected(self):
        res = requests.get(url='http://httpbin.org/ip',headers=self.headers,proxies=self.proxies)
        el = res.text
        try:
            res = json.loads(el)
            if ('origin' in res) & (res['origin']==self.proxy_ip.split(':')[0]):
                print('verified origin',res['origin'])
                self.is_working = True
        except:
            self.is_working = False

        if self.use_proxy:
            if not self.is_working:
                print('Connection failed' )
                self.proxy.blacklist(self.proxy_ip)
                print(f'proxy {self.proxy_ip} removed from rotation' )
                self.reconnect()
            else:
                print('Connection OK', self.proxy_ip)
                self.crawl_cnt = 0
        else:
            if not self.is_working:
                print('Connection failed' )                
            else:
                print('Connection OK - NO PROXY')

    def reconnect(self):
        if self.use_proxy:
            if self.crawl_cnt > self.crawl_limit:
                self.is_working = False

            while (not self.is_working):
                self.proxy_ip = self.proxy.rotate_proxy()
                # proxy with login
                ip,port,user,pwd = self.proxy_ip.split(':')
                self.proxies = {'http': f'http://{user}:{pwd}@{ip}:{port}/'}
                # verify
                self.is_connected()
        else:
            self.proxies = None

    def run(self,url):
        self.response = requests.get(url=url,headers=self.headers,proxies=self.proxies)
        self.response.status_code
        
        self.crawl_cnt += 1
        self.reconnect()

        return self.response.text


s= Static()
print(s.run('https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/lodzkie/lodz/lodz/lodz?distanceRadius=0&viewType=listing&limit=72&page=3'))

