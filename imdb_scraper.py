import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
import itertools
import datetime
from fuzzywuzzy import fuzz
import os
from os import listdir


def main():
    path = os.path.abspath(os.getcwd()) + '/flixpatrol_output'
    filenames = listdir(path)
    files = [ filename for filename in filenames if filename.endswith( '.csv' ) ]
    for f in files:
        scrape_imdb(f'./flixpatrol_output/{f}')

def scrape_imdb(csv):
    # Import CSV data
    data = pd.read_csv(csv)
    data = data.values.tolist()
    data = list(itertools.chain(*data))
    data = [*set(data)]

    # Initialize dict with titles
    titles = {}
    for d in data:
        titles[d] = ''

    for key in titles:
        # Alternate URL if more metadata is provided
        # url = f'https://www.imdb.com/search/title/?title={key}&release_date={int(years[key]) - 1}' + ',' + f'{int(years[key]) + 1}-01-01&title_type=feature&certificates=US%3AG,US%3APG,US%3APG-13,US%3AR,US%3ANC-17'

        url = f'https://www.imdb.com/search/title/?title={key}&title_type=feature,documentary,tvmovie,tvspecial,tv_miniseries,video&release_date=1960-01-01,{str(datetime.datetime.today())[:-19]}-30'

        if(titles[key] == ''):
            try:
                reference = requests.get(url, timeout=5)
                soup = BeautifulSoup(reference.text, 'html.parser')
            except:
                try:
                    reference = requests.get(url, timeout=5)
                    soup = BeautifulSoup(reference.text, 'html.parser')
                except:
                    continue
            movie_list = soup.find_all("div", {"class": "lister-item mode-advanced"})
            try:
                ## Safe approach ##
                if(len(movie_list) == 1):
                    titles[key] = str((re.search('tt[0-9]+', movie_list[0].find('h3').a['href'])).group(0))

                else:
                    ## Less safe approach ##
                    i = 0
                    while(fuzz.ratio(re.findall(">.*<", str(movie_list[i].find('h3').a))[0][1:-1], key.title()) < 80):
                        i+=1

                    titles[key] = str((re.search('tt[0-9]+', movie_list[i].find('h3').a['href'])).group(0))

            except:
                titles[key] = 'MISSING'


    df=pd.DataFrame.from_dict(titles, orient='index')
    name = re.findall('t/.*\.', csv)[0][2:-1]
    df.columns = ['imdb_id']
    df.index.name = 'title'
    df.to_csv(f"./flixpatrol_output/{name}imdb.csv")

if __name__ == "__main__":
    main()