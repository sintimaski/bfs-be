from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
import time
from bs4 import BeautifulSoup


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(
    "/usr/lib/chromium-browser/chromedriver", options=chrome_options
)

starting_business = "Hero"
url = "https://www.google.com/maps/search/" + starting_business
driver.get(url)
# time.sleep(10)

section_css_selector = "div.section-layout.section-scrollbox.scrollable-y.scrollable-show.section-layout-flex-vertical"
WebDriverWait(driver, 25).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, ""))
)

buisnesses = driver.find_elements_by_css_selector(
    f"{section_css_selector} div"
).click()
for buisness in buisnesses:
    soup = BeautifulSoup("html.parser", buisness)

# driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button').click()
# WebDriverWait(driver,25).until(EC.visibility_of_element_located((By.CLASS_NAME, "section-result-title")))
# hours = []
# hours.append([i.get_attribute('aria-label') for i in driver.find_elements_by_xpath("//*[contains(@aria-label, 'busy at')]")])
# print(hours)

with open("test.html", "w+") as file:
    file.write(driver.page_source)

driver.quit()


# scrollable_div = driver.find_element_by_css_selector(
#  'div.section-layout.section-scrollbox.scrollable-y.scrollable-show'
#                      )
# driver.execute_script(
#                'arguments[0].scrollTop = arguments[0].scrollHeight',
#                 scrollable_div
#                )
