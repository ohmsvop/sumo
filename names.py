import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
import romkan

df = pd.read_csv('names.txt')

names_dict = dict()
for index, row in df.iterrows():
    names_dict[row[0]] = row[1]


def kanji2hirakana(name):
    '''given a name in kanji, 
    return the name in hirakana
    by search in the wikipedia'''

    # find names in wikipedia
    domain = 'https://ja.wikipedia.org/wiki/'

    r = requests.get(domain + name)
    s = BeautifulSoup(r.text, "lxml")

    s = s.select('#mw-content-text')[0]
    s = s.select('p')[0].text

    pattern = r'（(.*?)、'
    name_hirakana = re.search(pattern, s).group(1)

    return name_hirakana

if __name__ == "__main__":
    # demo
    name = '錦木徹也'
    kanji2hirakana(name)

    file_names = open("names.txt",'a')

    name = '輝大士'
    if name not in names_dict.keys():
        hirakana = kanji2hirakana(name)
        romaji = romkan.to_roma(hirakana)
        print(hirakana)
        print(romaji)
        file_names.write(name+","+hirakana+"\n")

    file_names.close()

