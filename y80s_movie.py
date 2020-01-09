#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
from queue import Queue
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import redis
import re
import json

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'

thread_max_num = threading.Semaphore(50)

HEADERS = {
    'User-Agent': user_agent
}

redis_client = redis.Redis(db=8)
redis_client_9 = redis.Redis(db=9)


class Y80s:
    def __init__(self):
        self._type_name = 'movie'
        self._content_list = '/movie/list/-----p'
        self._base_url = 'http://www.y80s.com'
        self._page_sum = self.get_all_movie_page_number()

    def get_all_movie_page_number(self):
        """
        获取所有的页数
        """
        res = requests.get(self._base_url + self._content_list + '1', headers=HEADERS)
        soup = BeautifulSoup(res.content, 'html.parser')

        pager = soup.find_all('div', class_='pager')
        last_page = pager[0].find_all('a')[-1]
        last_page_href = last_page['href'].split('--p')
        all_page = last_page_href[-1]
        return int(all_page)

    def get_all_movie_list_url(self):
        return (self._base_url + self._content_list + str(x) for x in range(1, self._page_sum + 1))

    # 获取所有的 page
    def get_all_movie_page(self, url):
        req = requests.get(url, headers=HEADERS)

        soup = BeautifulSoup(req.content, 'html.parser')
        ul_list = soup.find_all('ul', class_='me1 clearfix')

        a_list = ul_list[0].find_all('a', attrs={
            'title': True
        })

        for x in a_list:
            redis_client.hset(self._type_name, x['title'], x['href'])


class Y80sMovie:
    def __init__(self):
        self._type_name = 'movie'
        self._content_list = '/movie/list/-----p'
        self._base_url = 'http://www.y80s.com'

    def open_movie_page(self, dl_info):

        title, url = dl_info[0], dl_info[1]

        req = requests.get(self._base_url + url, headers=HEADERS)
        soup = BeautifulSoup(req.content, 'html.parser')
        mp4_link = soup.find_all('a', attrs={
            'href': re.compile('^http://.*.mp4')
        })
        thunder_link = soup.find_all('a', attrs={
            'href': re.compile('thunder://')
        })
        data = {
            'title': title,
            'url': self._base_url + url,
            'mp4': [x['href'] for x in mp4_link],
            'thunder': [x['href'] for x in thunder_link]
        }
        redis_client_9.set(title, json.dumps(data))


if __name__ == '__main__':
    # task_queue = Queue(20)
    # y80s = Y80s()
    # movie_page = y80s.get_all_movie_list_url()
    # p = multiprocessing.Pool(multiprocessing.cpu_count())
    # p.map_async(y80s.get_all_movie_page, movie_page)
    # p.close()
    # p.join()

    y80s_movie = Y80sMovie()

    all_pages = redis_client.hgetall('movie')
    all_pages = [[x.decode('utf-8'), all_pages[x].decode('utf-8')] for x in all_pages.keys()]
    with ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(y80s_movie.open_movie_page, all_pages)

