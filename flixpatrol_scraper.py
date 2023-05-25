from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import datetime
import pandas as pd
import re

# Does not include itunes, google, vudu
streaming_services = ['netflix', 'hbo', 'disney', 'hulu', 'amazon']

finish_date = str(datetime.datetime.today())[:-16]
week = datetime.timedelta(days=7)

for s in streaming_services:

    data = {}
    
    curr_date = '2020-12-27'

    while(curr_date < finish_date):

        url = f'https://flixpatrol.com/top10/{s}/united-states/{curr_date}/'

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        browser.get(url)
        html = browser.page_source 
        content = BeautifulSoup(html, 'html.parser')
        table = content.find_all('table', {'class':'card-table'})[0]
        ranked_list = table.find_all('a', {'class':'hover:underline'})
        ranked_list = [ re.findall(">.*<", str(film))[0][1:-1] for film in ranked_list ]

        data[curr_date] = ranked_list

        curr_date = str(datetime.datetime.strptime(curr_date, '%Y-%m-%d') + week)[:-9]

        browser.quit()

    df = pd.DataFrame.from_dict(data,orient='index').transpose()
    df.to_csv(f'./flixpatrol_output/{s}.csv', index=False)

