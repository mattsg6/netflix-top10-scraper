from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import datetime
import pandas as pd
import re

base_url = 'https://top10.netflix.com/films'

curr_week = '2021-07-04'
finish_week = str(datetime.datetime.today())[:-16]
test_week = '2021-08-31'
week = datetime.timedelta(days=7)

data = {}

while(curr_week < finish_week):
    # Update URL
    url = base_url + f'?week={curr_week}'
    print(url)

    # Scrape site
    # response = requests.get(url, timeout=(15, 15))
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get(url)
    timeout = 30
    WebDriverWait(browser, timeout).until(ec.visibility_of_all_elements_located((By.ID, 'weekly-lists')))
    WebDriverWait(browser, timeout).until(ec.visibility_of_all_elements_located((By.ID, 'global-reach')))
    WebDriverWait(browser, timeout).until(ec.visibility_of_all_elements_located((By.ID, 'top-matter')))
    WebDriverWait(browser, timeout).until(ec.visibility_of_all_elements_located((By.ID, 'maincontent')))
    WebDriverWait(browser, timeout).until(ec.presence_of_element_located((By.ID, 'share-button')))
    WebDriverWait(browser, timeout).until(ec.presence_of_element_located((By.ID, 'end-matter')))
    html = browser.page_source 
    content = BeautifulSoup(html, 'html.parser')

    # Get film table
    film_list = content.find('table', {'class':'w-full text-sm table-fixed md:text-base'})
    td_tags = list(film_list.find_all('td', {'class':'pb-2 font-600 text-sm xs:text-base sm:text-lg leading-tight'}))
    td_tags.insert(0, content.find('td', {'class':'pb-2 font-600 text-sm xs:text-base sm:text-lg leading-tight pt-2'}))

    # Format data
    data[curr_week] = [ re.findall(">.*<", str(f))[0][1:-1] for f in td_tags ]

    # Check output
    # print(data)

    # Get next week
    curr_week = str(datetime.datetime.strptime(curr_week, '%Y-%m-%d') + week)[:-9]

    browser.quit()

df = pd.DataFrame.from_dict(data,orient='index').transpose()
df.to_csv('output.csv')