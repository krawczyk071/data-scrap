from selenium.webdriver.common.by import By

class MainPageLocators():
    """A class for main page locators. All main page locators should come here"""
    COOKIE = (By.ID, 'onetrust-accept-btn-handler')
    BOTTOM = (By.CSS_SELECTOR, '[data-cy="pagination"]')
    PAGINATIONS = (By.CSS_SELECTOR, '[data-cy^="pagination.go-to-page-"]')
    organic = ('[data-cy="search.listing.organic"]')
    itms = ('[data-cy="listing-item"]')
    link = ('[data-cy="listing-item-link"]')
    article = ('article')
    name = ('div h3')
    where = ('div + p')
    data = ('div:nth-of-type(2)')
    price = ('span:nth-of-type(1)')
    perm = ('span:nth-of-type(2)')
    rooms = ('span:nth-of-type(3)')
    sqm = ('span:nth-of-type(4)')
    who = ('div:nth-of-type(3)')

class DetailPageLocators():
    """A class for search results locators. All search results locators should
    come here"""

    footer = (By.CSS_SELECTOR, 'footer')
    show = ('[data-cy="phone-number.show-full-number-button"]')
    show_parent = show.find_element(By.XPATH, '..')
    modal = ('[data-cy="close-modal"]')
    more = ( By.CSS_SELECTOR, '[data-testid="content-container"]+button')
    contact = ('[data-cy="contact-form"]')
    author = ('div>span')
    tel = ('[data-cy="phone-number.full-phone-number"]')
    info = ('[data-testid="ad.top-information.table"]>div>div')
    infoA = ('div:nth-of-type(1)')
    infoB = ('div:nth-of-type(2)')
    full = ('[data-cy="adPageAdDescription"]')
    info2 = ('[data-testid="ad.additional-information.table"]>div>div')
    info2A = ('div:nth-of-type(1)')
    info2B = ('div:nth-of-type(2)')
    map = ('map>area')
    last = ('div:has(+#baxter-a-bottom)>div')
    imgs = ('.image-gallery-thumbnails-container img')
