from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from time import sleep

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

# download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in the
# current directory
chrome_driver = os.getcwd() +"/data/chromedriver"

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

"""
    上证 50: http://quote.eastmoney.com/zs000016.html
    沪深 300: http://quote.eastmoney.com/zs000300.html
    中证 500: http://quote.eastmoney.com/zs399905.html
"""

DATA_SROUCE = {
    'IH': 'http://quote.eastmoney.com/zs000016.html',
    'IC': 'http://quote.eastmoney.com/zs399905.html',
    'IF': 'http://quote.eastmoney.com/zs000300.html'
}
def fetch_data(code):
    driver.get(DATA_SROUCE[code])
    sleep(0.5)
    data = driver.find_element_by_css_selector("#price9").text;
    return data
