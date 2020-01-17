#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import tabula

url = 'https://www.hko.gov.hk/tc/gts/time/conversion.htm'
BASE_URL = 'https://www.hko.gov.hk/'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
base_path = '../data/'

req = requests.get(url, headers=headers)

soup = BeautifulSoup(req.content, 'html.parser')
pdf_links = soup.find_all('a', attrs={
    'href': re.compile('.*.pdf')
})


def download_lunar_pdf(url_id):
    href_url = url_id.get('href')
    href_url = href_url.split('../')[-1]

    os.chdir(base_path)

    with open(base_path + url_id.string + '.pdf', 'wb') as f:
        req = requests.get(BASE_URL + href_url, headers=headers)
        f.write(req.content)
        f.close()


with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(download_lunar_pdf, pdf_links)

all_pdf_files = os.listdir(base_path)
for pdf_file in all_pdf_files:
    if not os.path.isdir(base_path + pdf_file):
        if os.path.splitext(base_path + pdf_file)[-1] != '.pdf':
            continue
        tabula.convert_into(base_path + pdf_file, base_path + pdf_file + '.csv', output_format="csv")
