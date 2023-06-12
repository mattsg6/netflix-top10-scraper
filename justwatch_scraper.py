from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import re

services = ['max', 'netflix', 'amazon-prime-video', 'disney-plus', 'apple-tv-plus', 'hulu', 'peacock', 'paramount-plus', 'amc-plus', 'criterion-channel', 'starz', 'showtime']

for s in services:
    url = f'https://www.justwatch.com/us/provider/{s}/movies'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get(url)

    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            footer = browser.find_element(By.CLASS_NAME, 'timeline__end-of-timeline')
            break
        except:
            continue

    html = browser.page_source 
    content = BeautifulSoup(html, 'html.parser')
    data = content.find_all('a', {'class': 'title-list-grid__item--link'})

    res = []
    for d in data:
        title: str = re.findall("e/.*", d['href'])[0][2:]
        res.append(title.replace("-", " ").title())

    print(f'{s}: {len(res)}')

    df = pd.DataFrame(res, columns=['title'])
    df.to_csv(f'./justwatch_output/{s}.csv', index=False)

    browser.quit()