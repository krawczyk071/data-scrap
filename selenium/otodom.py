# %%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os

# Instantiate options
opts = Options()
# opts.add_argument(" — headless") # Uncomment if the headless version needed
# opts.binary_location = "<path to Chrome executable>"

# Instantiate a webdriver
driver = webdriver.Chrome(options=opts)

# Load the HTML page
def make_url(woj,miasto,page=1):
    return f'https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/{woj}/{miasto}/{miasto}/{miasto}?distanceRadius=0&viewType=listing&limit=72&page={page}'

driver.get(make_url('lodzkie','lodz'))

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

 # %%
print(driver.title)

try:
    acc = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    acc.click()
except:
    pass
# %%
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'[data-cy="pagination"]'))
    )
    print('Pagination OK')

except:
    # driver.quit()
    print('Pagination not OK')

# %%
organic = driver.find_element(By.CSS_SELECTOR,'[data-cy="search.listing.organic"]')
itms = organic.find_elements(By.CSS_SELECTOR,'[data-cy="listing-item"]')
for item in itms:

    link = item.find_element(By.CSS_SELECTOR,'[data-cy="listing-item-link"]')
    print(link.text)
# %%
# pagination = driver.find_element(By.CSS_SELECTOR,'[data-cy="pagination"]')
paginations = driver.find_elements(By.CSS_SELECTOR,'[data-cy^="pagination.go-to-page-"]')
last = int(paginations[-1].text)
# %%
