#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 15:14:50 2016

@author: ignacio
"""
import json
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import names
import romkan

domain = 'http://www.sumo.or.jp'
url = 'http://www.sumo.or.jp/ResultBanzuke/table_ajax'
payload = {'kakuzuke_id':'1',
           'basho_id':'579',
           'page':'1'}
headers = {'X-Requested-With': 'XMLHttpRequest'}
#session = requests.session()
r = requests.post(url, data = payload, headers=headers)

r = json.loads(r.text)
r = r['Html']

data = []

s = BeautifulSoup(r, "lxml")
s_row = s.select("tr")

month = s.select("p")[0].text.split()[0]
banzuke_type = s.select(".dayNum")[0].text.split()[0]

# contest table
contest = []

for n in range(1,len(s_row)):
    people_east = dict()
    s_column = s_row[n].select("td")[0]
    people_east["text"] = s_column.text.split()
    people_east["img"] = s_column.select("img")[0].attrs['src']
    
    banzuke = s_row[n].select("td")[1].text
    
    people_west = dict()
    s_column = s_row[n].select("td")[2]
    people_west["text"] = s_column.text.split()
    people_west["img"] = s_column.select("img")[0].attrs['src']
    
    contest.append([people_east, banzuke, people_west])

images = os.listdir("img")

# Downloads the images
for row in contest:
    for i in [0,2]: 
        url = domain + row[i]['img']
        name = os.path.basename(url)
        if name not in images: # check if already downloaded
            response = requests.get(url)
            if response.status_code == 200:
                f = open("img/" + name, 'wb')
                f.write(response.content)
                f.close()

# update the names.txt
df = pd.read_csv('names.txt')
file_names = open("names.txt",'a')

names_dict = dict()
for index, row in df.iterrows():
    names_dict[row[0]] = row[1]

for row in contest:
    for i in [0,2]:
        try:
            name = row[i]['text'][0]+row[i]['text'][1]
            if name not in names_dict.keys():
                hirakana = names.kanji2hirakana(name)
                file_names.write(name+","+hirakana+"\n")
        except:
            pass

file_names.close()

# Write in the docx
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

document = Document()
document.add_heading('番付表', 0)
paragraph = document.add_paragraph(month)
paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
document.add_heading(banzuke_type, level=1)

table = document.add_table(1, 5)
table.style = 'TableGrid'
table.autofit = False
table.rows[0].cells[0].text = '東'
table.rows[0].cells[2].text = '番付'
table.rows[0].cells[3].text = '西'


for row in contest:
    row_cells = table.add_row().cells
    for j in [0,1]:
        img_name = os.path.basename(row[j*2]['img']) # j = 0,2
        text = ''
        if img_name:
            run = row_cells[j*3].paragraphs[0].add_run()
            run.add_picture('img/' + img_name, width = 600000, height = 600000)

            description = list(row[j*2]['text'])# j = 0,2
            name = description[0]+description[1]
            hirakana = names_dict[name]
            romaji = romkan.to_roma(hirakana)
            description.insert(2,hirakana)
            description.insert(3,romaji)
            text = '{0} {1}\n{2}\n{3}\n{4}{5}{6}'.format(*description)

        row_cells[j*3+1].text = text # j = 1,4
    row_cells[2].text = row[1]

# set the table width
table.autofit = False
for i in [0,3]:
    table.columns[i].width = 650000
    for cell in table.column_cells(i):
        cell.width = 650000
table.columns[2].width = 500000
for cell in table.column_cells(2):
    cell.width = 500000
for i in [1,4]:
    table.columns[i].width = 1800000
    for cell in table.column_cells(i):
        cell.width = 1800000

document.save('docx/'+month+'_'+banzuke_type+'.docx')
