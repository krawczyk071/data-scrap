from elements import BasePageElement
from locators import MainPageLocators,DetailPageLocators
from utils import Parser,Crawler
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import WebDriverWait


class BasePage():
    """Base class to initialize the base page that will be called from all
    pages"""

    def __init__(self, driver,writer,**kwargs):
        self.driver = driver
        self.writer = writer
        self.update_last = kwargs.get('update_last',None)
        self.page_now = kwargs.get('page',None)
        self.url = kwargs.get('link',None)

    def find_se(self, locator):
        try:
            #  WebDriverWait(driver, 10).until(EC.presence_of_element_located(*self.locator)
            element = self.driver.find_element(*locator)
            return element
        except:
            print(f'element with {locator} not present')


# class CookieElement(BasePageElement):
#     """This class gets the search text from the specified locator"""

#     # The locator for search box where search string is entered
#     locator = MainPageLocators.COOKIE


# class BottomElement(BasePageElement):
#     locator = MainPageLocators.BOTTOM



class MainPage(BasePage):
    """Home page action methods come here. I.e. Python.org"""

    # Declares a variable that will contain the retrieved text
    # search_text_element = SearchTextElement()

    # def is_title_matches(self):
    #     """Verifies that the hardcoded text "Python" appears in page title"""

    #     return "Python" in self.driver.title

    def make_url(self, woj, miasto, page=1):
        return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'

    def start(self,woj,miasto):
        self.driver.get(self.make_url(woj, miasto, page=self.page_now))

    def click_cookie(self):
        try:
            element = self.find_se(MainPageLocators.COOKIE)
            element.click()
        except:
            pass
    def get_page_info(self):
        paginations = self.driver.find_elements(*MainPageLocators.PAGINATIONS)
        # self.page_last = int(paginations[-1].text)
        self.update_last(int(paginations[-1].text))

    def scroll_load(self):
        try:
            # element = BottomElement()
            element = self.driver.find_element(*MainPageLocators.BOTTOM)

            ActionChains(self.driver).move_to_element(element).perform()
            return True
        except:
            return False


    def get_html(self):
        self.html = self.driver.page_source
    
    def parse(self):

        dom = Parser(self.html, "html.parser")
        organic = dom.select_one(MainPageLocators.organic)

        date = time.strftime("%Y%m%d")

        itms = organic.select(MainPageLocators.itms)

        for item in itms:

            estate_data = dict()

            estate_data['date'] = date
            link = item.select_one(MainPageLocators.link)
            estate_data['link'] = link["href"]

            article = item.select_one(MainPageLocators.article)
            estate_data['name'] = article.select_one(MainPageLocators.name).text
            estate_data['where'] = article.select_one(MainPageLocators.where).text
            estate_data['who'] = article.select_one(MainPageLocators.who).text

            data = article.select_one(MainPageLocators.data)
            estate_data['price'] = data.select_one(MainPageLocators.price).text
            estate_data['perm'] = data.select_one(MainPageLocators.perm).text
            estate_data['rooms'] = data.select_one(MainPageLocators.rooms).text
            estate_data['sqm'] = data.select_one(MainPageLocators.sqm).text
            # export
            self.writer.save_row(estate_data)

class DetailPage(BasePage):

    def start(self):
        self.driver.get(self.url)

    def click_cookie(self):
        try:
            element = self.find_se(MainPageLocators.COOKIE)
            element.click()
        except:
            pass
    def scroll_load(self):
        try:
            element = self.driver.find_element(*DetailPageLocators.footer)
            ActionChains(self.driver).move_to_element(element).perform()
            return True
        except:
            return False
        
    def check_active(self):
        try:
            self.driver.find_element(*DetailPageLocators.inactive)
            # save empty row
            estate_data = dict()
            estate_data['date'] = time.strftime("%Y%m%d")
            estate_data['link'] = self.url
            estate_data['full'] = 'INACTIVE'
            self.writer.save_row(estate_data)
            return False
        except:
            return True
        
    def waitCSS(self,locator, where):
        return WebDriverWait(where, 3).until(EC.presence_of_element_located(locator))

    # show tel
    def telshow(self):
        show = self.waitCSS(DetailPageLocators.show, self.driver)

        show_parent = show.find_element(*DetailPageLocators.show_parent)
        while ('Pokaż numer'.lower() in show_parent.text.lower()):
            try:
                show = self.driver.find_element(*DetailPageLocators.show)
                ActionChains(self.driver).move_to_element(show).click(show).perform()
                self.modal()
            except:
                pass

    def modal(self):
    # hide modal for agencies
        try:
            modal = self.waitCSS(DetailPageLocators.modal, self.driver)
            modal.click()
            self.telshow()
        except:
            pass

    def details(self):
        # show more details if exists
        try:
            more = self.driver.find_element(*DetailPageLocators.more)
            ActionChains(self.driver).move_to_element(more).click(more).perform()
        except:
            pass


    # selenium end
    def get_html(self):
        self.html = self.driver.page_source
    
    def parse(self):

        dom = Parser(self.html, "html.parser")

        estate_data = dict()
        estate_data['date'] = time.strftime("%Y%m%d")
        estate_data['link'] = self.url

        contact = dom.select_one(DetailPageLocators.contact)
        estate_data['author'] = contact.select_one(DetailPageLocators.author).text

        estate_data['tel'] = contact.select_one(DetailPageLocators.tel).text

        info = dom.select(DetailPageLocators.info)
        for ii in info:
            ii1 = ii.select_one(DetailPageLocators.infoA).text
            ii2 = ii.select_one(DetailPageLocators.infoB).text
            estate_data[ii1] = ii2

        estate_data['full'] = dom.select_one(DetailPageLocators.full).text

        info2 = dom.select(DetailPageLocators.info2)
        for ii in info2:
            ii1 = ii.select_one(DetailPageLocators.info2A).text
            ii2 = ii.select_one(DetailPageLocators.info2B).text
            estate_data[ii1] = ii2

        # map = dom.select_one(DetailPageLocators.map).text['coords']

        last = dom.select(DetailPageLocators.last)
        for l in last:
            try:
                if ':' in l.text:
                    k, v = l.text.split(':')
                else:
                    k, v = l.text.split('nieruchomości')
                estate_data[k] = v.strip()
            except:
                pass

        imgs = dom.select(DetailPageLocators.imgs)
        estate_data['imgs'] = [x['src'] for x in imgs]

        # export
        self.writer.save_row(estate_data)