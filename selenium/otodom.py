# %%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os

def init():
    # Instantiate options
    opts = Options()
    # opts.add_argument(" — headless") # Uncomment if the headless version needed
    # opts.binary_location = "<path to Chrome executable>"

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts)
    return driver
driver = init()

def make_url(woj,miasto,page=1):
        return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'

    
# # Parse processed webpage with BeautifulSoup
# soup = BeautifulSoup(driver.page_source)
# print(soup.find(id="test").get_text())

# select elements by class name 
# elements = driver.find_elements(By.CLASS_NAME, 'text-container') 
# for title in elements: 
# 	# select H2s, within element, by tag name 
# 	heading = title.find_element(By.TAG_NAME, 'h2').text 
# 	# print H2s 
# 	print(heading)

def cookie():
    try:
        acc = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
        acc.click()
    except:
        print('no cookie')

def is_loaded():
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'[data-cy="pagination"]'))
        )
        return True
    except:
        return False
    
def first():
    driver.get(make_url('lodzkie','lodz'))
    paginations = driver.find_elements(By.CSS_SELECTOR,'[data-cy^="pagination.go-to-page-"]')
    last = int(paginations[-1].text)
    return last

def top(page=1):
    driver.get(make_url('lodzkie','lodz',page))
    cookie()

    if not is_loaded():
        print('not loaded')
        return
    
    organic = driver.find_element(By.CSS_SELECTOR,'[data-cy="search.listing.organic"]')
    itms = organic.find_elements(By.CSS_SELECTOR,'[data-cy="listing-item"]')
    for item in itms:

        link = item.find_element(By.CSS_SELECTOR,'[data-cy="listing-item-link"]')
        article = item.find_element(By.CSS_SELECTOR,'article')
        link = link.get_attribute('href')
        name = article.find_element(By.CSS_SELECTOR,'div h3').text
        where = article.find_element(By.CSS_SELECTOR,'div + p').text
        data = article.find_element(By.CSS_SELECTOR,'div:nth-of-type(2)')
        price = data.find_element(By.CSS_SELECTOR,'span:nth-of-type(1)').text
        perm = data.find_element(By.CSS_SELECTOR,'span:nth-of-type(2)').text
        rooms = data.find_element(By.CSS_SELECTOR,'span:nth-of-type(3)').text
        sqm = data.find_element(By.CSS_SELECTOR,'span:nth-of-type(4)').text
        who = article.find_element(By.CSS_SELECTOR,'div:nth-of-type(3)').text
        
        print(who)                                                                                  


def details(url='https://www.otodom.pl/pl/oferta/2-pokoje-44m-umeblowane-klima-do-wprowadzenia-ID4ka0Q'):
    driver.get(url)
    cookie()

    contact = driver.find_element(By.CSS_SELECTOR,'[data-cy="contact-form"]')
    author = contact.find_element(By.CSS_SELECTOR,'div>span').text
    #opt
    show = driver.find_element(By.CSS_SELECTOR,'[data-cy="phone-number.show-full-number-button"]')
    show.click()
    tel = driver.find_element(By.CSS_SELECTOR,'[data-cy="phone-number.full-phone-number"]').text

    info = driver.find_elements(By.CSS_SELECTOR,'[data-testid="ad.top-information.table"]>div>div')
    for ii in info:
        ii1 = ii.find_element(By.CSS_SELECTOR,'div:nth-of-type(1)').text
        ii2 = ii.find_element(By.CSS_SELECTOR,'div:nth-of-type(2)').text
        # print(ii1,ii2)
    #opt
    more = driver.find_element(By.CSS_SELECTOR,'[data-testid="content-container"]+button')
    webdriver.ActionChains(driver).move_to_element(more).click(more).perform()
    full = driver.find_element(By.CSS_SELECTOR,'[data-cy="adPageAdDescription"]').text

    info2 = driver.find_elements(By.CSS_SELECTOR,'[data-testid="ad.additional-information.table"]>div>div')
    for ii in info2:
        ii1 = ii.find_element(By.CSS_SELECTOR,'div:nth-of-type(1)').text
        ii2 = ii.find_element(By.CSS_SELECTOR,'div:nth-of-type(2)').text
        # print(ii1,ii2)
    # map = driver.find_element(By.CSS_SELECTOR,'map>area').get_attribute('coords')
    last = driver.find_elements(By.CSS_SELECTOR,'[data-cy="ad.avm-module.container"]+ h2 + div>div')
    for l in last:
        # print(l.text)
        pass
    imgs = driver.find_elements(By.CSS_SELECTOR,'.image-gallery-thumbnails-container img')
    for img in imgs:
        iurl = img.get_attribute('src')
        # print(iurl)

init()
# first()
top()
# details()