from bs4 import BeautifulSoup
import random
from exporter import Ecsv

class Parser(BeautifulSoup):
    pass
    # soup = BeautifulSoup(self.html, "html.parser")
    # organic = soup.select_one(MainPageLocators.organic)
    # itms = organic.select(MainPageLocators.itms)

class Crawler():
    pass

class Proxy():
    def __init__(self):
        self.load_list()

    def load_list(self):
        reader = Ecsv(mode='r',filename='./proxylist.csv')
        self.ips = [row['proxy'] for row in reader.rows]

    def rand_proxy(self):
        try:
            proxy = random.choice(self.ips)
        except IndexError:
            print('Proxy list is empty')    
        return proxy
    
    def blacklist(self,ip):
        self.ips.remove(ip)