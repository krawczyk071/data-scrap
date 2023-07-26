from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePageElement():
    """Base page class that is initialized on every page object class."""

    def __set__(self, obj, value):
        """Sets the text to the value supplied"""

        driver = obj.driver
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(*self.locator))
        driver.find_element(*self.locator).clear()
        driver.find_element(*self.locator).send_keys(value)

    def __get__(self, obj, owner):
        """Gets the text of the specified object"""

        driver = obj.driver
        # try:
        #     WebDriverWait(driver, 10).until(
        #         lambda driver: driver.find_element(*self.locator))
        #     #  WebDriverWait(driver, 10).until(EC.presence_of_element_located(*self.locator)
        #     element = driver.find_element(*self.locator)
        #     return element.get_attribute("value")
        #     # print(element)
        #     # return element
        # except:
        #     print(f'element with {self.locator} not present')

        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element(*self.locator))
        element = driver.find_element(*self.locator)
        return element.get_attribute("value")
