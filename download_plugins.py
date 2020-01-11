#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
import threading

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'

headers = {'User-Agent': user_agent}

url = 'https://github.com/qbittorrent/search-plugins/wiki/Unofficial-search-plugins'

res = requests.get(url, headers=headers)

soup = BeautifulSoup(res.content, 'html.parser')

py_link = soup.find_all('a', attrs={'href': re.compile('https://.*.py')})


def download_file(url):
    href_link = url['href']
    file_name = href_link.split('/')[-1]
    with open(file_name, 'wb') as f:
        print('downloading: {}'.format(href_link))
        req = requests.get(href_link, headers=headers)
        f.write(req.content)
        f.close()


all_threads = []
for x in py_link:
    t = threading.Thread(target=download_file, args=(x, ))
    t.start()
    all_threads.append(t)

for x in all_threads:
    x.join()

print('downloaded')
