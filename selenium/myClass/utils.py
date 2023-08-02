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