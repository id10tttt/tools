#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import requests
import logging
import queue
import aiohttp
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

requests.packages.urllib3.disable_warnings()

_logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}


def logger_cost_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        _logger.info({
            'cost time: ': time.time() - start_time
        })
        print('cost: ', time.time() - start_time)
        return res

    return wrapper


def make_sum():
    ts_num = 0
    while True:
        yield ts_num
        ts_num += 1


class ThreadPoolExecutorWithQueueSizeLimit(ThreadPoolExecutor):
    def __init__(self, max_workers=None, *args, **kwargs):
        super().__init__(max_workers, *args, **kwargs)
        self._work_queue = queue.Queue(max_workers * 2)


class M3U8Download(object):
    def __init__(self, m3u8_url=None, m3u8_filename=None, max_retries=5, max_workers=40):
        self._m3u8_url = m3u8_url
        self._max_retries = max_retries
        self._m3u8_ts_list = []
        self.headers = DEFAULT_HEADERS
        self.front_url = None
        self._m3u8_file_name = m3u8_filename
        self._max_workers = max_workers
        self.ts_sum = 0
        self.success_sum = 0
        self.fetch_m3u8_info(m3u8_url, max_retries)
        self._chunk_size = 1024

    def fetch_m3u8_info(self, m3u8_url, num_retries):
        """
        fetch m3u8 data
        """
        try:
            res = requests.get(m3u8_url, timeout=(3, 30), verify=False, headers=self.headers)
            self.front_url = res.url.split(res.request.path_url)[0]
            if "EXT-X-STREAM-INF" in res.text:
                for line in res.text.split('\n'):
                    if "#" in line or not line:
                        continue
                    elif re.search(r'^http', line) is not None:
                        self._m3u8_url = line
                    elif re.search(r'^/', line) is not None:
                        self._m3u8_url = self.front_url + line
                    else:
                        self._m3u8_url = self._m3u8_url.rsplit("/", 1)[0] + '/' + line
                self.fetch_m3u8_info(self._m3u8_url, self._max_retries)
            else:
                m3u8_text_str = res.text
                self.fetch_m3u8_ts_url(m3u8_text_str)
        except Exception as e:
            print(e)
            if num_retries > 0:
                self.fetch_m3u8_info(m3u8_url, num_retries - 1)

    def fetch_m3u8_ts_url(self, m3u8_text_str):
        """
        fetch ts url
        """
        if not os.path.exists(f"./{self._m3u8_file_name}"):
            os.mkdir(f"./{self._m3u8_file_name}")
        new_m3u8_str = ''
        ts = make_sum()
        for line in m3u8_text_str.split('\n'):
            if "#" in line:
                if "EXT-X-KEY" in line and "URI=" in line:
                    key = self.download_key(line, 5)
                    if key:
                        new_m3u8_str += f'{key}\n'
                        continue
                new_m3u8_str += f'{line}\n'
                if "EXT-X-ENDLIST" in line:
                    break
            elif re.search(r'^http', line) is not None:
                new_m3u8_str += f"./{self._m3u8_file_name}/{next(ts)}\n"
                self._m3u8_ts_list.append(line)
            elif re.search(r'^/', line) is not None:
                new_m3u8_str += f"./{self._m3u8_file_name}/{next(ts)}\n"
                self._m3u8_ts_list.append(self.front_url + line)
            else:
                new_m3u8_str += f"./{self._m3u8_file_name}/{next(ts)}\n"
                self._m3u8_ts_list.append(self._m3u8_url.rsplit("/", 1)[0] + '/' + line)
        self.ts_sum = next(ts)
        with open(f"./{self._m3u8_file_name}.m3u8", "w") as f:
            f.write(new_m3u8_str)

    def download_ts(self, ts_url, save_ts_name, num_retries):
        """
        download ts file
        """
        ts_url = ts_url.split('\n')[0]
        try:
            if not os.path.exists(f"./{self._m3u8_file_name}/{save_ts_name}"):
                res = requests.get(ts_url, stream=True, timeout=(5, 60), verify=False, headers=self.headers)
                if res.status_code == 200:
                    with open(f"./{self._m3u8_file_name}/{save_ts_name}", "wb") as ts:
                        for chunk in res.iter_content(chunk_size=1024):
                            if chunk:
                                ts.write(chunk)
                    self.success_sum += 1
                    print(f"\rDownloading {self._m3u8_file_name}：{self.success_sum}/{self.ts_sum}\t", end='')
                else:
                    self.download_ts(ts_url, save_ts_name, num_retries - 1)
                res.close()
            else:
                self.success_sum += 1
        except Exception:
            if os.path.exists(f"./{self._m3u8_file_name}/{save_ts_name}"):
                os.remove(f"./{self._m3u8_file_name}/{save_ts_name}")
            if num_retries > 0:
                self.download_ts(ts_url, save_ts_name, num_retries - 1)

    def download_key(self, key_line, num_retries):
        """
        下载key文件
        """
        mid_part = re.search(r"URI=[\'|\"].*?[\'|\"]", key_line).group()
        may_key_url = mid_part[5:-1]
        if re.search(r'^http', may_key_url) is not None:
            true_key_url = may_key_url
        elif re.search(r'^/', may_key_url) is not None:
            true_key_url = self.front_url + may_key_url
        else:
            true_key_url = self._m3u8_url.rsplit("/", 1)[0] + '/' + may_key_url
        try:
            res = requests.get(true_key_url, timeout=(5, 60), verify=False, headers=self.headers)
            with open(f"./{self._m3u8_file_name}/key", 'wb') as f:
                f.write(res.content)
            res.close()
            return f'{key_line.split(mid_part)[0]}URI="./{self._m3u8_file_name}/key"{key_line.split(mid_part)[-1]}'
        except Exception as e:
            print(e)
            if os.path.exists(f"./{self._m3u8_file_name}/key"):
                os.remove(f"./{self._m3u8_file_name}/key")
            print("加密视频,无法加载key,揭秘失败")
            if num_retries > 0:
                self.download_key(key_line, num_retries - 1)

    def merge_ts_to_mp4(self):
        """
        合并.ts文件，输出mp4格式视频，需要ffmpeg
        """
        cmd = f"ffmpeg -allowed_extensions ALL -i {self._m3u8_file_name}.m3u8 -acodec copy -vcodec copy -f mp4 {self._m3u8_file_name}.mp4"
        os.system(cmd)
        # os.system(f'rm -rf ./{self._m3u8_file_name} ./{self._m3u8_file_name}.m3u8')
        print(f"Download successfully --> {self._m3u8_file_name}")

    async def save_resp_content_to_file(self, resp, ts_file_obj):
        while True:
            chunk_file = await resp.content.read(self._chunk_size)
            if not chunk_file:
                break
            ts_file_obj.write(chunk_file)

    async def _m3u8_download_ts(self, ts_url, save_ts_name, max_retry):
        async with aiohttp.ClientSession() as session:
            async with session.get(ts_url) as resp:
                if resp.status == 200:
                    with open(f"./{self._m3u8_file_name}/{save_ts_name}", "wb") as ts:
                        await self.save_resp_content_to_file(resp, ts)

                    self.success_sum += 1
                    print(f"\rDownloading {self._m3u8_file_name}：{self.success_sum}/{self.ts_sum}\t", end='')
                else:
                    self.download_ts(ts_url, save_ts_name, max_retry - 1)
                resp.close()

    async def m3u8_download_ts(self, ts_url, save_ts_name, max_retry):
        try:
            ts_url = ts_url.split('\n')[0]
            if not os.path.exists(f"./{self._m3u8_file_name}/{save_ts_name}"):
                await self._m3u8_download_ts(ts_url, save_ts_name, max_retry)
            else:
                self.success_sum += 1
        except Exception as e:
            if os.path.exists(f"./{self._m3u8_file_name}/{save_ts_name}"):
                os.remove(f"./{self._m3u8_file_name}/{save_ts_name}")
            if max_retry > 0:
                await self.m3u8_download_ts(ts_url, save_ts_name, max_retry - 1)

    async def main(self, ts_url, index_ts, sem):
        async with sem:
            await self.m3u8_download_ts(ts_url, index_ts, self._max_retries)

    @logger_cost_time
    def start_download(self):
        loop = asyncio.get_event_loop()
        _sem = asyncio.Semaphore(self._max_workers)
        tasks = []
        for _index_ts, _ts_url in enumerate(self._m3u8_ts_list):
            tasks.append(
                loop.create_task(self.main(_ts_url, _index_ts, _sem))
            )
        loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == '__main__':
    try:
        m3u8_link = sys.argv[1]
        m3u8_filename = sys.argv[2]
    except IndexError:
        m3u8_link = 'https://bk.andisk.com/data/3048aa1f-b2fb-4fb7-b452-3ebc96c76374/res/' \
                    'f1826fdb-def2-4dba-a7a1-4afbf5d17491.m3u8'
        m3u8_filename = str(time.time())
        # m3u8_link = 'https://v.zdubo.com/20200115/FkoHzMWM/index.m3u8'

    download_client = M3U8Download(m3u8_url=m3u8_link, m3u8_filename=m3u8_filename, max_retries=5, max_workers=120)
    download_client.start_download()
