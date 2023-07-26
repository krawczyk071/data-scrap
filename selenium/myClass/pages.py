from elements import BasePageElement
from locators import MainPageLocators
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    def __init__(self, driver):
        self.driver = driver

    def find(self, locator):
        try:
            #  WebDriverWait(driver, 10).until(EC.presence_of_element_located(*self.locator)
            element = self.driver.find_element(*locator)
            return element
        except:
            print(f'element with {locator} not present')


class CookieElement(BasePageElement):
    """This class gets the search text from the specified locator"""

    # The locator for search box where search string is entered
    locator = MainPageLocators.COOKIE


class BottomElement(BasePageElement):
    locator = MainPageLocators.BOTTOM


class MainPage(BasePage):
    """Home page action methods come here. I.e. Python.org"""

    # Declares a variable that will contain the retrieved text
    # search_text_element = SearchTextElement()

    # def is_title_matches(self):
    #     """Verifies that the hardcoded text "Python" appears in page title"""

    #     return "Python" in self.driver.title

    def make_url(woj, miasto, page=1):
        return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'

    def start(self):
        self.driver.get(self.make_url('lodzkie', 'lodz'))

    def click_cookie(self):
        try:
            element = self.find(MainPageLocators.COOKIE)
            element.click()
        except:
            pass

    def scroll_load(self):
        try:
            # element = BottomElement()
            element = self.driver.find_element(*MainPageLocators.BOTTOM)

            ActionChains(self.driver).move_to_element(element).perform()
            print('donme')
            return True
        except:
            print('not donme')
            return False

    def get_page_info(self):
        paginations = self.driver.find_element(*MainPageLocators.PAGINATIONS)
        self.last = int(paginations[-1].text)
