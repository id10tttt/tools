#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import m3u8
import os
from Crypto.Cipher import AES
from multiprocessing import Pool
import multiprocessing
import requests

import threading
import queue

import aiohttp
import asyncio
import aiofiles

import time

# 信号量
sem = asyncio.Semaphore(30)

headers = {
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
}


def get_m3u8_key_iv(m3u8_obj):
    try:
        key_context, iv_context = requests.get(m3u8_obj.base_uri + m3u8_obj.keys[0].uri).content, m3u8_obj.keys[0].iv
        key_context = key_context.decode('utf-8')
    except Exception as e:
        key_context, iv_context = False, False

    return key_context, iv_context


# 多进程
def download_m3u8(m3u8_url):
    m3u8_obj = m3u8.load(m3u8_url, headers=headers)
    base_path = mkdir_m3u8_file(m3u8_obj)

    pool = Pool(processes=multiprocessing.cpu_count())
    # pool.map_async(download_m3u8_ts_file, m3u8_obj.segments)

    key_context, iv_context = get_m3u8_key_iv(m3u8_obj)

    for index_m3u8, m3u8_obj_segments in enumerate(m3u8_obj.segments):
        pool.apply_async(download_m3u8_ts_file,
                         args=(base_path, m3u8_obj_segments, str(index_m3u8 + 1), key_context, iv_context))
    pool.close()
    pool.join()

    merge_ts_2_mp4(base_path)


# 下载文件
def download_m3u8_ts_file(base_path, m3u8_obj_segments, index_m3u8, key_context, iv_context):
    ts_link, ts_name = m3u8_obj_segments.base_uri + m3u8_obj_segments.uri, m3u8_obj_segments.uri
    # with open(base_path + index_m3u8 + '.ts', 'wb') as f:
    with open(base_path + ts_name, 'wb') as f:
        tmp = requests.get(ts_link, headers=headers)
        tmp_data = tmp.content

        # 解密
        if key_context:
            decrypt_data = decrypt_ts_file(tmp_data, key_context, iv_context)
        else:
            decrypt_data = tmp_data
        print('download: ', index_m3u8)
        f.write(decrypt_data)


# 创建文件夹
def mkdir_m3u8_file(m3u8_obj):
    base_uri = m3u8_obj.base_uri
    base_path = base_uri.replace('/', '').replace(':', '')
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    return base_path + '/'


# 异步下载
async def download_m3u8_async(m3u8_url):
    m3u8_obj = m3u8.load(m3u8_url, headers=headers)
    base_path = mkdir_m3u8_file(m3u8_obj)
    for index_m3u8, m3u8_obj_segments in enumerate(m3u8_obj.segments):
        ts_link, ts_name = m3u8_obj_segments.base_uri + m3u8_obj_segments.uri, m3u8_obj_segments.uri
        await download_m3u8_ts_file_async(base_path, ts_link, str(index_m3u8))

    merge_ts_2_mp4(base_path)


# 异步下载
async def download_m3u8_ts_file_async(base_path, ts_link, index_m3u8):
    async with aiohttp.ClientSession() as session:
        async with session.request('GET', ts_link, headers=headers) as resp:
            with open(base_path + index_m3u8 + '.ts', 'wb') as f:
                tmp = await resp.read()
                f.write(tmp)


async def fetch_url_link_file(url_link):
    async with aiohttp.ClientSession() as session:
        async with session.get(url_link, headers=headers) as resp:
            html = await resp.read()
            return html


# 下载
def main_download_m3u8(urls):
    loop = asyncio.get_event_loop()
    tasks = [download_m3u8_async(url) for url in urls]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


# 多线程下载
def download_m3u8_multi_threading(m3u8_url):
    m3u8_obj = m3u8.load(m3u8_url, headers=headers)
    base_path = mkdir_m3u8_file(m3u8_obj)
    key_context, iv_context = get_m3u8_key_iv(m3u8_obj)
    thread_ids = []
    for index_m3u8, m3u8_obj_segments in enumerate(m3u8_obj.segments):
        t = threading.Thread(target=download_m3u8_ts_file,
                             args=(base_path, m3u8_obj_segments, str(index_m3u8 + 1), key_context, iv_context))
        t.start()
        thread_ids.append(t)
    for x in thread_ids:
        x.join()

    merge_ts_2_mp4(base_path)


# 多线程下载 queue
def download_m3u8_multi_threading_queue(m3u8_url):
    m3u8_obj = m3u8.load(m3u8_url, headers=headers)

    q = queue.Queue()
    thread_ids = []
    for m3u8_obj_segments in m3u8_obj.segments:
        t = threading.Thread(target=download_m3u8_ts_file_queue, args=(m3u8_obj_segments, q))
        t.start()
        thread_ids.append(t)
    for x in thread_ids:
        x.join()

    result = []
    while not q.empty():
        result.append(q.get())
    print('result: ', result)


def download_m3u8_ts_file_queue(m3u8_obj_segments, queue):
    ts_link, ts_name = m3u8_obj_segments.base_uri + m3u8_obj_segments.uri, m3u8_obj_segments.uri
    with open(ts_name, 'wb') as f:
        tmp = requests.get(ts_link, headers=headers)
        f.write(tmp.content)
    queue.put(ts_link)


# 合并
def merge_ts_2_mp4(base_path):
    os.chdir(base_path)
    merge_file = 'for ts_id in `ls | sort -n`; do cat $ts_id >> all.mp4; done'

    # ls -1v sort by name
    merge_file = 'for ts_id in `ls -1v`; do cat $ts_id >> all.mp4; done'
    os.system(merge_file)
    # os.system('rm *.ts')


def decrypt_ts_file(data, key, iv):
    print('key: ', key, 'iv: ', iv)
    decryptor = AES.new(key, AES.MODE_CBC, IV=iv)
    return decryptor.decrypt(data)


if __name__ == '__main__':
    urls = ["https://72vod.150564.com/201907/7166d4f5/index.m3u8"]
    urls = ["https://bk.andisk.com/data/3048aa1f-b2fb-4fb7-b452-3ebc96c76374/res/f1826fdb-def2-4dba-a7a1-4afbf5d17491.m3u8"]
    # urls = ["https://m3u8.cdnpan.com/SyRXtKTd.m3u8"]
    # urls = ["https://yiqikan.wuyouzuida.com/20190907/287_cec142d9/index.m3u8"]
    start_time = time.time()
    # main_download_m3u8(urls)
    download_m3u8(urls[0])
    # download_m3u8_multi_threading(urls[0])
    # download_m3u8_multi_threading_queue(urls[0])
    print('cost: ', time.time() - start_time)
