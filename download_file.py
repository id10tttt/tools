#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import threading
import math

sem = threading.Semaphore(20)

# 每次下载的大小
chunk_size = 1099983

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}
file_url = 'http://anning.luanniao-zuida.com/1912/%E8%AF%AF%E6%9D%80.TC%E6%B8%85%E6%99%B0v3%E7%89%88.mp4'

file_url = 'http://down.phpzuida.com/2001/%E5%BE%B7%E5%8F%A4%E6%8B%892020-03.mp4'


def get_file_size(download_url):
    r = requests.head(download_url, headers=headers)
    size = int(r.headers['Content-Length'])
    return size


def split_part_size(size_number, part_size):
    if part_size > part_size:
        return 0, part_size
    tmp = []

    current_size = 0
    for x in range(0, size_number, part_size):
        if current_size > size_number:
            continue
        current_part = [current_size + 1, current_size + part_size]
        current_size += part_size
        if current_size > size_number:
            current_part[1] = size_number
        tmp.append(current_part)
    return tmp


def download_part_file(url, start, end, index_part, base_path):
    headers = {
        'Range': 'bytes={}-{}'.format(start, end),
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

    req = requests.get(url, headers=headers, stream=True)

    with open(base_path + index_part + '.part', 'wb') as f:
        f.write(req.content)
    sem.release()


def merge_file_to_mp4(base_path):
    os.chdir(base_path)
    merge_file = 'for file_id in `ls | sort -n`; do cat $file_id >> all.mp4; done'
    os.system(merge_file)
    os.system('rm *.part')


base_path = file_url.replace('/', '').replace(':', '').replace('%', '').replace('.', '')
base_path = base_path + '/'
if not os.path.exists(base_path):
    os.mkdir(base_path)

thread_ids = []
size = get_file_size(file_url)
split_size = split_part_size(size, chunk_size)
with sem:
    for index_part, part_size in enumerate(split_size):
        sem.acquire()
        t = threading.Thread(target=download_part_file,
                             args=(file_url, part_size[0], part_size[1], str(index_part + 1), base_path))
        t.start()
        thread_ids.append(t)

for t in thread_ids:
    t.join()

merge_file_to_mp4(base_path)
