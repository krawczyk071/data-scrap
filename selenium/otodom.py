# %%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import os
import csv
import time


def init():
    # Instantiate options
    opts = Options()
    # opts.add_argument(" — headless") # Uncomment if the headless version needed
    # opts.binary_location = "<path to Chrome executable>"

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts)
    return driver


driver = init()


def make_url(woj, miasto, page=1):
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
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-cy="pagination"]'))
        )
        return True
    except:
        return False


def first():
    driver.get(make_url('lodzkie', 'lodz'))
    paginations = driver.find_elements(
        By.CSS_SELECTOR, '[data-cy^="pagination.go-to-page-"]')
    last = int(paginations[-1].text)
    return last


def create_csv(fieldnames):

    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = './output'+timestr+'.csv'

    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
    return filename


def save_csv(filename, fieldnames, row):
    with open(filename, 'a', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writerow(row)


def top(filename, fieldnames, page=1):
    driver.get(make_url('lodzkie', 'lodz', page))
    cookie()

    if not is_loaded():
        print('not loaded')
        return

    organic = driver.find_element(
        By.CSS_SELECTOR, '[data-cy="search.listing.organic"]')
    itms = organic.find_elements(By.CSS_SELECTOR, '[data-cy="listing-item"]')
    date = time.strftime("%Y%m%d")
    for item in itms:

        estate_data = dict()
        estate_data['date'] = date
        link = item.find_element(
            By.CSS_SELECTOR, '[data-cy="listing-item-link"]')
        article = item.find_element(By.CSS_SELECTOR, 'article')
        estate_data['link'] = link.get_attribute('href')
        estate_data['name'] = article.find_element(
            By.CSS_SELECTOR, 'div h3').text
        estate_data['where'] = article.find_element(
            By.CSS_SELECTOR, 'div + p').text
        data = article.find_element(By.CSS_SELECTOR, 'div:nth-of-type(2)')
        estate_data['price'] = data.find_element(
            By.CSS_SELECTOR, 'span:nth-of-type(1)').text
        estate_data['perm'] = data.find_element(
            By.CSS_SELECTOR, 'span:nth-of-type(2)').text
        estate_data['rooms'] = data.find_element(
            By.CSS_SELECTOR, 'span:nth-of-type(3)').text
        estate_data['sqm'] = data.find_element(
            By.CSS_SELECTOR, 'span:nth-of-type(4)').text
        estate_data['who'] = article.find_element(
            By.CSS_SELECTOR, 'div:nth-of-type(3)').text

        # with open(filename, 'a', encoding='UTF8', newline='') as f:
        #     writer = csv.DictWriter(f, fieldnames=fieldnames)
        #     writer.writerow(estate_data)
        save_csv(filename, fieldnames, estate_data)


def waitCSS(css, where=driver):
    return WebDriverWait(where, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))


def details(filename, fieldnames, url='https://www.otodom.pl/pl/oferta/2-pokoje-44m-umeblowane-klima-do-wprowadzenia-ID4ka0Q',):
    driver.get(url)
    cookie()

    estate_data = dict()
    estate_data['date'] = time.strftime("%Y%m%d")
    estate_data['link'] = url

    contact = driver.find_element(By.CSS_SELECTOR, '[data-cy="contact-form"]')
    estate_data['author'] = contact.find_element(
        By.CSS_SELECTOR, 'div>span').text

    # opt
    # show = driver.find_element(
    #     By.CSS_SELECTOR, '[data-cy="phone-number.show-full-number-button"]')
    # show.click()
    show = waitCSS('[data-cy="phone-number.show-full-number-button"]')
    ActionChains(driver).move_to_element(show).click(show).perform()
    try:
        # modal = driver.find_element(By.CSS_SELECTOR, '[data-cy="close-modal"]')
        # modal = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        #     (By.CSS_SELECTOR, '[data-cy="close-modal"]')))
        # modal.click()
        waitCSS('[data-cy="close-modal"]').click()
    except:
        pass

    # estate_data['tel'] = driver.find_element(
    #     By.CSS_SELECTOR, '[data-cy="phone-number.full-phone-number"]').text
    estate_data['tel'] = waitCSS(
        '[data-cy="phone-number.full-phone-number"]').text

    info = driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="ad.top-information.table"]>div>div')
    for ii in info:
        ii1 = ii.find_element(By.CSS_SELECTOR, 'div:nth-of-type(1)').text
        ii2 = ii.find_element(By.CSS_SELECTOR, 'div:nth-of-type(2)').text
        estate_data[ii1] = ii2
        if ii1 == '':
            print(1, ii.text)
        # print(ii1,ii2)

    # opt
    try:
        more = driver.find_element(
            By.CSS_SELECTOR, '[data-testid="content-container"]+button')
        ActionChains(driver).move_to_element(more).click(more).perform()
    except:
        pass

    estate_data['full'] = driver.find_element(
        By.CSS_SELECTOR, '[data-cy="adPageAdDescription"]').text

    info2 = driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="ad.additional-information.table"]>div>div')
    for ii in info2:
        ii1 = ii.find_element(By.CSS_SELECTOR, 'div:nth-of-type(1)').text
        ii2 = ii.find_element(By.CSS_SELECTOR, 'div:nth-of-type(2)').text
        estate_data[ii1] = ii2
        # print(ii1,ii2)

    # map = driver.find_element(By.CSS_SELECTOR,'map>area').get_attribute('coords')
    # last = driver.find_elements(By.CSS_SELECTOR,'[data-cy="ad.avm-module.container"]+ h2 + div>div')
    last = driver.find_elements(
        By.CSS_SELECTOR, 'div:has(+#baxter-a-bottom)>div')
    for l in last:
        # print(l.text)
        try:
            if ':' in l.text:
                k, v = l.text.split(':')
            else:
                # print(l.text)
                k, v = l.text.split('nieruchomości')

            estate_data[k] = v.strip()
        except:
            pass

    imgs = driver.find_elements(
        By.CSS_SELECTOR, '.image-gallery-thumbnails-container img')
    # for img in imgs:
    #     iurl = img.get_attribute('src')
    # print(iurl)
    estate_data['imgs'] = [x.get_attribute('src') for x in imgs]

    # print(estate_data)
    save_csv(filename, fieldnames, estate_data)


def main1():
    init()
    fieldnames = ['date', 'link', 'name', 'where',
                  'price', 'perm', 'rooms', 'sqm', 'who']
    filename = create_csv(fieldnames)
    pages = range(1, first()+1)
    # pages = range(1, 3)
    for page in pages:
        top(filename, fieldnames, page)


def main2():
    links = ['https://www.otodom.pl/pl/oferta/mieszkanie-22-50-m-lodz-ID4iIbp',
             'https://www.otodom.pl/pl/oferta/mieszkanie-m3-lanowa-37m2-teofilow-bezposrednio-ID4ll0F',
             'https://www.otodom.pl/pl/oferta/apartamenty-zolnierska-12-aa-2-ID4lVwG']
    init()
    fieldnames = ['link', 'Nr oferty w biurze ', 'date', 'imgs', 'tel', 'Piętro', 'Czynsz', 'Okna', 'Typ ogłoszeniodawcy', 'Rynek', 'Ogrzewanie',
                  'Materiał budynku', 'Rodzaj zabudowy', 'author', 'Miejsce parkingowe', 'Rok budowy', 'Stan wykończenia', 'Liczba pokoi', 'Dostępne od', 'Winda', 'Wyposażenie', 'Zabezpieczenia', 'Media', 'Balkon / ogród / taras', 'Informacje dodatkowe', 'Forma własności', 'full', 'Obsługa zdalna', 'Powierzchnia', 'Nr oferty w Otodom', 'Data dodania', 'Data aktualizacji']
    filename = create_csv(fieldnames)

    # details(filename,fieldnames)
    for link in links:
        details(filename, fieldnames, link)


main1()
# main2()

# top()
# details()

# # csv header
# fieldnames = ['name', 'area', 'country_code2', 'country_code3']

# # csv data
# rows = [
#     {'name': 'Albania',
#     'area': 28748,
#     'country_code2': 'AL',
#     'country_code3': 'ALB'},
#     {'name': 'Algeria',
#     'area': 2381741,
#     'country_code2': 'DZ',
#     'country_code3': 'DZA'}
# ]

# def save_csv(filename,fieldnames)
#     with open(filename, 'w', encoding='UTF8', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(rows)
