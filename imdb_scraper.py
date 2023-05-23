import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
import itertools
import datetime
from fuzzywuzzy import fuzz

# Import CSV data
data = pd.read_csv('output.csv')
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
            # if(len(movie_list) == 1):
            #     titles[key] = str((re.search('tt[0-9]+', movie_list[0].find('h3').a['href'])).group(0))
            # else:
            #     titles[key] = ''

            ## Fast approach ##
            i = 0
            while(fuzz.ratio(re.findall(">.*<", str(movie_list[i].find('h3').a))[0][1:-1], key) < 80):
                i+=1

            titles[key] = str((re.search('tt[0-9]+', movie_list[i].find('h3').a['href'])).group(0))

        except:
            titles[key] = 'MISSING'


df=pd.DataFrame.from_dict(titles, orient='index')
df.to_csv("imdb.csv")

# Note on results
# 428/438 IDs were matched (97.7% fill rate)
# The remaining 10 were added to the CSV by hand
# 2/10 were a result of not including 'video' in title_type
# 8/10 were the result of title names
# Ex. Dr Suess' The Lorax (Netflix) // The Lorax (IMDb)