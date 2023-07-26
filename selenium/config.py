import random

ips = ['95.216.114.142:80', '190.194.151.37:8080', '5.2.228.168:8888',
       '5.165.6.188:1513',	'61.7.146.7:80', '181.225.101.50:999']


def rand_proxy():
    proxy = random.choice(ips)
    return proxy
