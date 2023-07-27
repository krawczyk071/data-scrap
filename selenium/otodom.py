# %%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import csv
import time
import os
from config import rand_proxy


class Driver(webdriver.Chrome):
    def __init__(self, options):
        super().__init__(options)
        self.is_working = False

        self.options = Options()
        self.options.add_argument("--headless=new")
        self.options.add_argument('--proxy-server=95.216.114.142:80')


d = Driver()
d.get('http://onet.pl')
# %%


def is_connected():
    # driver.get('http://www.90minut.pl/')
    el = driver.find_element(By.TAG_NAME, 'body').text
    is_bad = 'ERR_TIMED_OUT' in el
    return not is_bad


def init():
    # Instantiate options
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("start-maximized")

    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.binary_location = "<path to Chrome executable>"

    # PROXY
    proxy = rand_proxy()
    options.add_argument(f'--proxy-server={proxy}')

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=options)

    return driver


# driver = init()
driver = None


def make_url(woj, miasto, page=1):
    return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'


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

        ActionChains(driver).move_to_element(element).perform()
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


def export_csv(name, data):

    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = './'+name+timestr+'.csv'

    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(data)
    return filename


def top(filename, fieldnames, page=1):
    driver.get(make_url('lodzkie', 'lodz', page))

    cookie()

    if not is_loaded():
        print('not loaded')
        return

    # selenium end
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, "html.parser")
    organic = soup.select('[data-cy="search.listing.organic"]')[0]

    date = time.strftime("%Y%m%d")

    itms = organic.select('[data-cy="listing-item"]')

    for item in itms:

        estate_data = dict()

        estate_data['date'] = date
        link = item.select('[data-cy="listing-item-link"]')[0]
        estate_data['link'] = link["href"]

        article = item.select('article')[0]
        estate_data['name'] = article.select('div h3')[0].text
        estate_data['where'] = article.select('div + p')[0].text

        data = article.select('div:nth-of-type(2)')[0]
        estate_data['price'] = data.select('span:nth-of-type(1)')[0].text
        estate_data['perm'] = data.select('span:nth-of-type(2)')[0].text
        estate_data['rooms'] = data.select('span:nth-of-type(3)')[0].text
        estate_data['sqm'] = data.select('span:nth-of-type(4)')[0].text
        estate_data['who'] = article.select('div:nth-of-type(3)')[0].text

        save_csv(filename, fieldnames, estate_data)


def waitCSS(css, where):
    return WebDriverWait(where, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))


def details(filename: str, fieldnames: list[str], url: str, driver) -> bool:
    is_reseted = False

    def verify(driver):
        driver.get(url)
        # abandon connection if not working
        if not is_connected():
            driver = None
            is_reseted = True
            return driver

    if driver:
        driver = verify(driver)

    while (not driver):
        # try to make connection
        init()
        driver = verify(driver)

    cookie()

    # scroll to bottom
    footer = driver.find_element(By.CSS_SELECTOR, 'footer')
    ActionChains(driver).scroll_to_element(footer).perform()
    # show tel
    show = waitCSS('[data-cy="phone-number.show-full-number-button"]', driver)
    show_parent = show.find_element(By.XPATH, '..')
    while ('Pokaż numer'.lower() in show_parent.text.lower()):
        try:
            show = driver.find_element(
                By.CSS_SELECTOR, '[data-cy="phone-number.show-full-number-button"]')
            show.click()
        except:
            pass

    # ActionChains(driver).move_to_element(show).click(show).perform()
    # try:
    #     show2 = waitCSS('[data-cy="phone-number.show-full-number-button"]')
    #     ActionChains(driver).move_to_element(show).click(show).perform()
    # except:
    #     pass
    # wait for tel to show
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    #     (By.CSS_SELECTOR, '[data-cy="phone-number.full-phone-number"]')))

    # hide modal for agencies
    try:
        waitCSS('[data-cy="close-modal"]', driver).click()
    except:
        pass
    # show more details if exists
    try:
        more = driver.find_element(
            By.CSS_SELECTOR, '[data-testid="content-container"]+button')
        ActionChains(driver).move_to_element(more).click(more).perform()
    except:
        pass

    # selenium end
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    estate_data = dict()
    estate_data['date'] = time.strftime("%Y%m%d")
    estate_data['link'] = url

    contact = soup.select('[data-cy="contact-form"]')[0]
    estate_data['author'] = contact.select('div>span')[0].text

    estate_data['tel'] = contact.select(
        '[data-cy="phone-number.full-phone-number"]')[0].text

    info = soup.select('[data-testid="ad.top-information.table"]>div>div')
    for ii in info:
        ii1 = ii.select('div:nth-of-type(1)')[0].text
        ii2 = ii.select('div:nth-of-type(2)')[0].text
        estate_data[ii1] = ii2

    estate_data['full'] = soup.select(
        '[data-cy="adPageAdDescription"]')[0].text

    info2 = soup.select(
        '[data-testid="ad.additional-information.table"]>div>div')
    for ii in info2:
        ii1 = ii.select('div:nth-of-type(1)')[0].text
        ii2 = ii.select('div:nth-of-type(2)')[0].text
        estate_data[ii1] = ii2

    # map = soup.select('map>area')[0]['coords']

    last = soup.select('div:has(+#baxter-a-bottom)>div')
    for l in last:
        try:
            if ':' in l.text:
                k, v = l.text.split(':')
            else:
                k, v = l.text.split('nieruchomości')

            estate_data[k] = v.strip()
        except:
            pass

    imgs = soup.select('.image-gallery-thumbnails-container img')
    estate_data['imgs'] = [x['src'] for x in imgs]

    save_csv(filename, fieldnames, estate_data)

    return is_reseted


def main1():
    init()
    fieldnames = ['date', 'link', 'name', 'where',
                  'price', 'perm', 'rooms', 'sqm', 'who']
    filename = create_csv(fieldnames)
    pages = range(1, first()+1)
    pages = range(1, 3)
    for page in pages:
        top(filename, fieldnames, page)


def main2(driver):
    links = ['https://www.otodom.pl/pl/oferta/mieszkanie-22-50-m-lodz-ID4iIbp',
             'https://www.otodom.pl/pl/oferta/mieszkanie-m3-lanowa-37m2-teofilow-bezposrednio-ID4ll0F',
             'https://www.otodom.pl/pl/oferta/apartamenty-zolnierska-12-aa-2-ID4lVwG']

    # init()
    fieldnames = ['link', 'Nr oferty w biurze ', 'date', 'imgs', 'tel', 'Piętro', 'Czynsz', 'Okna', 'Typ ogłoszeniodawcy', 'Rynek', 'Ogrzewanie',
                  'Materiał budynku', 'Rodzaj zabudowy', 'author', 'Miejsce parkingowe', 'Rok budowy', 'Stan wykończenia', 'Liczba pokoi', 'Dostępne od', 'Winda', 'Wyposażenie', 'Zabezpieczenia', 'Media', 'Balkon / ogród / taras', 'Informacje dodatkowe', 'Forma własności', 'full', 'Obsługa zdalna', 'Powierzchnia', 'Nr oferty w Otodom', 'Data dodania', 'Data aktualizacji']
    filename = create_csv(fieldnames)

    # details(filename,fieldnames)
    proxy_cnt = 0
    for link in links:

        if details(filename, fieldnames, link, driver):
            proxy_cnt = 0
        else:
            proxy_cnt += 1
            if proxy_cnt > 20:
                driver = None


# main1()
main2(driver)
