#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import time
import os

BASE_URL = 'http://www.bing.com'
DAILY_BING_IMAGE_URL = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=zh-CN'
IMAGE_TAIL = '_1920x1080.jpg'

BASE_HOME = os.environ['HOME']
BING_IMG_SAVE_PATH = '{}/Pictures/Bing/'.format(BASE_HOME)


class BingDownload(object):
    def __init__(self):
        self.base_url = BASE_URL
        self.image_tail = IMAGE_TAIL
        self.download_list = []
        self.base_download_path = BING_IMG_SAVE_PATH

    async def get_file_save_path(self):
        img_path = self.base_download_path
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        return img_path

    async def get_file_name(self, file_name):
        file_path = await self.get_file_save_path()
        file_path = file_path + file_name
        return file_path

    async def parse_fetch_image_id(self):
        fetch_image_id = DAILY_BING_IMAGE_URL
        return fetch_image_id

    async def main(self):
        fetch_image_id = await self.parse_fetch_image_id()
        await self.get_bing_daily_picture(fetch_image_id)

    async def get_bing_daily_picture(self, fetch_image_id):
        async with aiohttp.ClientSession() as session:
            resp = await session.get(fetch_image_id)
            res_dict = await resp.json()
            for image_id in res_dict.get('images'):
                image_urlbase = image_id.get('urlbase')
                start_date = image_id.get('startdate')
                if image_urlbase not in self.download_list:
                    self.download_list.append(image_urlbase)
                    await self.download_bing_picture(image_urlbase, session)
                else:
                    continue

    async def download_bing_picture(self, download_url, session):
        bing_download_url = self.base_url + download_url + self.image_tail
        file_name = bing_download_url.split('id=')[-1]
        file_name = await self.get_file_name(file_name)
        resp = await session.get(bing_download_url)
        content = await resp.read()
        with open(file_name, 'wb') as f:
            f.write(content)


if __name__ == '__main__':
    start_time = time.time()
    bing_downloader = BingDownload()
    asyncio.run(bing_downloader.main())
    print('cost: {}'.format(time.time() - start_time))
