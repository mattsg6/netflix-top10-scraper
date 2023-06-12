import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import time
from fuzzywuzzy import fuzz
import os
from os import listdir


def main():
    path = os.path.abspath(os.getcwd()) + '/justwatch_output'
    filenames = listdir(path)
    files = [ filename for filename in filenames if filename.endswith( '.csv' ) ]
    for f in files:
        scrape_imdb(f'./justwatch_output/{f}')

def scrape_imdb(csv):
    print(f'Starting {csv} -- {time.strftime("%H:%M:%S",time.localtime())}')

    # Import CSV data - Flix Patrol
    # data = pd.read_csv(csv)
    # data = data.values.tolist()
    # data = list(itertools.chain(*data))
    # data = [*set(data)]

    # Import CSV data - Justwatch
    data = pd.read_csv(csv)
    data = list(data['title'])

    # Initialize dict with titles
    titles = {}

    for key in data:
        url = ''

        try:
            year = int(key[-4:])
            key = key[:-5]
            url = f'https://www.imdb.com/search/title/?title={key}&title_type=feature,documentary,tvmovie,tvspecial,tv_miniseries,video&release_date={year - 1}-01-01,{year + 1}-12-31'

        except:
            url = f'https://www.imdb.com/search/title/?title={key}&title_type=feature,documentary,tvmovie,tvspecial,tv_miniseries,video&release_date=1930-01-01,{str(datetime.datetime.today())[:-19]}-30'

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
    df.to_csv(f"./justwatch_output/{name}_imdb.csv")

    print(f'Completed -- {time.strftime("%H:%M:%S",time.localtime())}')

if __name__ == "__main__":
    main()