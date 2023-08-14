from bs4 import BeautifulSoup
import random
from exporter import Ecsv
import requests, json
from random import randint
from time import sleep

class Parser(BeautifulSoup):
    def __init__(self,html,parser="html.parser"):
        super().__init__(html,parser)
    # soup = BeautifulSoup(self.html, "html.parser")
    # organic = soup.select_one(MainPageLocators.organic)
    # itms = organic.select(MainPageLocators.itms)

class Crawler():
    pass

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


