#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import m3u8
import os
import sys
from Crypto.Cipher import AES
from multiprocessing import Pool
import multiprocessing
import requests
import logging
import threading
import queue
import aiohttp
import asyncio
import time
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

_logger = logging.getLogger(__name__)

# 信号量
sem = asyncio.Semaphore(30)

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}


def logger_cost_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        _logger.info({
            'cost time: ': time.time() - start_time
        })
        print('cost: ', time.time() - start_time)
        return res

    return wrapper


class M3u8Download(object):
    def __init__(self, m3u8_url):
        self.m3u8_url = m3u8_url
        self.m3u8_obj = self.get_m3u8_obj()
        self._base_path = self.mkdir_m3u8_file()
        self.m3u8_key = self.get_m3u8_key_iv()[0]
        self.m3u8_iv = self.get_m3u8_key_iv()[1]

    # TODO: focus on diff resolution
    def get_m3u8_obj(self):
        """
        m3u8
        playlists: bandwidth and resolution
        :return: m3u8
        """
        m3u8_obj = m3u8.load(self.m3u8_url, headers=headers)
        if m3u8_obj.data.get('playlists', False):
            # TODO: for now, only one resolution
            for playlist_uri in m3u8_obj.data.get('playlists'):
                _logger.info({
                    'resolution': playlist_uri
                })
                url = m3u8_obj.base_uri + playlist_uri.get('uri')
                m3u8_obj = m3u8.load(url, headers=headers)
        return m3u8_obj

    def get_m3u8_key_iv(self):
        """
        获取 m3u8 的 key
        :return: 返回 key 和 iv
        """
        try:
            key_context, iv_context = requests.get(self.m3u8_obj.base_uri + self.m3u8_obj.keys[0].uri).content, \
                                      self.m3u8_obj.keys[0].iv
            key_context = key_context.decode('utf-8')
        except Exception as e:
            _logger.info({
                'error': e
            })
            key_context, iv_context = False, False

        return key_context, iv_context.decode('hex') if iv_context else iv_context

    def decrypt_ts_file(self, data):
        """
        解密 ts
        :param data: 数据
        :return: AES.MODE_CBC 解密后的数据
        """
        if self.m3u8_iv:
            decrypt_obj = AES.new(self.m3u8_key, AES.MODE_CBC, self.m3u8_key, iv=self.m3u8_iv)
        else:
            decrypt_obj = AES.new(self.m3u8_key, AES.MODE_CBC, self.m3u8_key)
        return decrypt_obj.decrypt(data)

    def mkdir_m3u8_file(self):
        """
        创建文件夹
        :return: 文件夹
        """
        base_uri = self.m3u8_obj.base_uri
        base_path = base_uri.replace('/', '').replace(':', '')
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        return base_path + '/'

    def merge_ts_2_mp4(self):
        """
        合并ts 为 mp4
        按照自然排序 ls -1v
        """
        os.chdir(self.base_path)
        # ls -1v sort by name
        merge_file = 'for ts_id in `ls -1v *.ts`; do cat $ts_id >> all.mp4; done'
        os.system(merge_file)
        os.system('rm *.ts')

    def download_m3u8_ts_file(self, m3u8_obj_segments):
        """
        下载文件
        :param m3u8_obj_segments: m3u8 ts 段
        """
        ts_link, ts_name = m3u8_obj_segments.base_uri + m3u8_obj_segments.uri, m3u8_obj_segments.uri
        print('ts_link, ts_name', ts_link, ts_name)
        with open(self.base_path + ts_name, 'wb') as f:
            tmp = requests.get(ts_link, headers=headers)
            tmp_data = tmp.content

            # 解密
            if self.m3u8_key:
                decrypt_data = self.decrypt_ts_file(tmp_data)
            else:
                decrypt_data = tmp_data
            _logger.info({
                'download file: ': ts_name
            })
            f.write(decrypt_data)

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, base_path):
        self._base_path = base_path


class MultiProcessM3u8Download(M3u8Download):
    """
    多进程下载
    """

    def __init__(self, m3u8_url):
        super(MultiProcessM3u8Download, self).__init__(m3u8_url)

    @logger_cost_time
    def download_m3u8_multi_process(self):
        """
        多进程下载 Pool(processes=multiprocessing.cpu_count())
        """
        pool = Pool(processes=multiprocessing.cpu_count())

        for m3u8_obj_segments in self.m3u8_obj.segments:
            pool.apply_async(self.download_m3u8_ts_file, args=(m3u8_obj_segments,))
        pool.close()
        pool.join()


class MultiThreadingM3u8Download(M3u8Download):
    """
    多线程下载
    """

    def __init__(self, m3u8_url):
        super(MultiThreadingM3u8Download, self).__init__(m3u8_url)

    @logger_cost_time
    def download_m3u8_multi_threading(self):
        # use ThreadPoolExecutor in case too many threader
        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(self.download_m3u8_ts_file, self.m3u8_obj.segments)

        # thread_ids = []
        # for m3u8_obj_segments in self.m3u8_obj.segments:
        #     t = threading.Thread(target=self.download_m3u8_ts_file, args=(m3u8_obj_segments,))
        #     t.start()
        #     thread_ids.append(t)
        # for x in thread_ids:
        #     x.join()


class MultiThreadingQueueM3u8Download(M3u8Download):
    """
    多线程队列
    """

    def __init__(self, m3u8_url):
        super(MultiThreadingQueueM3u8Download, self).__init__(m3u8_url)
        self.queue = queue.Queue()

    @logger_cost_time
    def download_m3u8_multi_threading_queue(self):
        """
        多线程下载 queue
        :return:
        """
        thread_ids = []
        for m3u8_obj_segments in self.m3u8_obj.segments:
            t = threading.Thread(target=self.download_m3u8_ts_file_queue, args=(m3u8_obj_segments,))
            t.start()
            thread_ids.append(t)
        for x in thread_ids:
            x.join()

        result = []
        while not self.queue.empty():
            result.append(self.queue.get())
        print('result: ', result)

    def download_m3u8_ts_file_queue(self, m3u8_obj_segments):
        ts_link, ts_name = m3u8_obj_segments.base_uri + m3u8_obj_segments.uri, m3u8_obj_segments.uri
        with open(self.base_path + ts_name, 'wb') as f:
            tmp = requests.get(ts_link, headers=headers)
            f.write(tmp.content)
        self.queue.put(ts_link)


class AsyncM3u8Download(M3u8Download):
    """
    异步多线程
    """

    def __init__(self, m3u8_url):
        super(AsyncM3u8Download, self).__init__(m3u8_url)

    # FIXME: 可能对异步的理解不对
    async def download_m3u8_ts_file_async(self, ts_link, ts_name):
        """
        异步下载
        :param ts_link: 下载的ts链接
        :param ts_name: 下载的名字
        """
        async with aiohttp.ClientSession() as session:
            async with session.request('GET', ts_link, headers=headers) as resp:
                with open(self.base_path + ts_name + '.ts', 'wb') as f:
                    tmp = await resp.read()
                    f.write(tmp)

    @logger_cost_time
    def main_download_m3u8(self):
        """
        下载的入口
        """
        tasks = []
        loop = asyncio.get_event_loop()
        for m3u8_obj_segments in self.m3u8_obj.segments:
            ts_link, ts_name = m3u8_obj_segments.base_uri + m3u8_obj_segments.uri, m3u8_obj_segments.uri
            tasks.append(self.download_m3u8_ts_file_async(ts_link, ts_name))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()


if __name__ == '__main__':

    try:
        m3u8_link = sys.argv[1]
    except IndexError:
        m3u8_link = 'https://bk.andisk.com/data/3048aa1f-b2fb-4fb7-b452-3ebc96c76374/res/' \
                    'f1826fdb-def2-4dba-a7a1-4afbf5d17491.m3u8'
        # m3u8_link = 'https://v.zdubo.com/20200115/FkoHzMWM/index.m3u8'

    # # 多进程下载
    # downloader = MultiProcessM3u8Download(m3u8_link)
    # downloader.download_m3u8_multi_process()
    # downloader.merge_ts_2_mp4()

    # # 多线程下载
    downloader = MultiThreadingM3u8Download(m3u8_link)
    downloader.download_m3u8_multi_threading()
    downloader.merge_ts_2_mp4()

    # # 多线程队列
    # downloader = MultiThreadingQueueM3u8Download(m3u8_link)
    # downloader.download_m3u8_multi_threading_queue()
    # downloader.merge_ts_2_mp4()

    # # 异步多线程
    # downloader = AsyncM3u8Download(m3u8_link)
    # downloader.main_download_m3u8()
    # downloader.merge_ts_2_mp4()
