# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox, QAbstractItemView, QFileDialog
from PyQt5.QtCore import QStringListModel
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2 import QtCore
import math
import asyncio
import aiohttp
import re
import logging
import os
import requests
import time

_logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
}

TS_HEADERS = ['名称', '链接', '是否下载']


def compute_sum():
    ts_num = 0
    while True:
        yield ts_num
        ts_num += 1


class DownloadM3U8QtUI(QWidget):
    def __init__(self):
        self.ui = QUiLoader().load('download_m3u8.ui')
        self.ts_sum = 0
        self.success_sum = 0
        self._max_workers = 128
        self._m3u8_ts_list = []
        self._max_retries = 5
        self._m3u8_file_name = str(time.time())
        self.front_url = ''
        self._m3u8_url = ''
        self._chunk_size = 1024
        self.headers = DEFAULT_HEADERS

        self.model_table_list = QStandardItemModel(0, 3)

        self.initial_download_table()

        self.ui.start_download_button.clicked.connect(self.start_download_file)
        self.ui.button_open_folder.clicked.connect(self.open_folder)
        self.ui.download_list_table.doubleClicked.connect(self.check_download_list_ts)

        self.ui.download_file_name_input.textChanged.connect(self.update_download_m3u8_file_name)

        self.ui.button_merge_ts_to_mp4.clicked.connect(self.merge_m3u8_ts_2_mp4)
        # self.loop = QEventLoop()
        # asyncio.set_event_loop(self.loop)

    def get_default_model_table_list(self):
        model_table_list = QStandardItemModel(0, 3)
        model_table_list.setHorizontalHeaderLabels(TS_HEADERS)
        return model_table_list

    def update_download_m3u8_file_name(self):
        if self.ui.download_file_name_input.text():
            self._m3u8_file_name = self.ui.download_file_name_input.text()
            self.initial_download_table()

    def update_download_max_workers(self):
        if self.ui.max_async_count_input.text():
            self._max_workers = int(self.ui.max_async_count_input.text())

    def initial_download_table(self):
        self.model_table_list = self.get_default_model_table_list()
        self.ui.download_list_table.horizontalHeader().setStretchLastSection(True)
        self.ui.download_list_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.download_list_table.setModel(self.model_table_list)

        self.ui.download_progress.setValue(0)

    # 下载文件的保存路径
    def open_folder(self):
        directory = QFileDialog.getExistingDirectory()
        self.ui.download_file_path_input.setText(directory)
        self.initial_download_table()

    def check_download_list_ts(self, model_index):
        select_data = self.model_table_list.data(self.model_table_list.index(model_index.row(), 1))
        # QMessageBox.information(self, '提示', '选中: {}'.format(select_data))
        self.msg_notifaction('选中: {}'.format(select_data), '选中: {}'.format(select_data))

    def parse_download_ts_list(self):
        self.fetch_m3u8_ts_info(self._max_retries)
        self.set_download_table_view()

    async def _start_download_ts_file(self, ts_url, file_name, max_sem):
        async with max_sem:
            return await self.m3u8_download_ts(ts_url, file_name, self._max_retries)

    def _start_download_file(self):
        max_sem = asyncio.Semaphore(self._max_workers)
        tasks = []
        for _index_ts, _ts_url in enumerate(self._m3u8_ts_list):
            tasks.append(
                asyncio.ensure_future(self._start_download_ts_file(_ts_url, _index_ts, max_sem)))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        execute_results = []
        for task in tasks:
            execute_results.append(task.result())
        loop.close()
        self.ui.start_download_button.setEnabled(True)
        self.ui.button_merge_ts_to_mp4.setEnabled(True)
        self.msg_notifaction('下载成功', execute_results, success_state=True)

    # 开始下载
    def start_download_file(self):
        self.ui.start_download_button.setEnabled(False)
        self.ui.button_merge_ts_to_mp4.setEnabled(False)
        self.update_download_m3u8_file_name()
        self.update_download_max_workers()

        self.parse_download_ts_list()
        self._start_download_file()

    # 合并TS 为 MP4, 使用 ffmpeg
    def merge_m3u8_ts_2_mp4(self):
        if self.ui.download_progress.text() != '100%':
            self.msg_notifaction('Wait a minute...', '稍等片刻，还在下载...')
        else:
            self.merge_ts_to_mp4()

    def msg_notifaction(self, notif_msg, detail_msg, success_state=False):
        msg_box = QMessageBox()
        if success_state:
            msg_box.setIcon(QMessageBox.Information)
        else:
            msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText('{}'.format(notif_msg))
        msg_box.setDetailedText('{}'.format(detail_msg))
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.show()
        msg_box.exec()

    def merge_ts_to_mp4(self):

        new_m3u8_file = self.get_new_m3u8_file()
        merge_mp4_file = self.get_m3u8_ts_merge_mp4_file()

        file_folder = self.get_save_ts_file_folder()

        merge_cmd = 'ffmpeg -allowed_extensions ALL -i {new_m3u8_file} ' \
                    '-acodec copy -vcodec copy -f mp4 {merge_mp4_file}'.format(
            new_m3u8_file=new_m3u8_file,
            merge_mp4_file=merge_mp4_file
        )
        os.system(merge_cmd)
        # os.system(f'rm -rf {file_folder} {new_m3u8_file}')

    def fetch_m3u8_ts_info(self, max_retries):
        if self.ui.download_url_input.text():
            m3u8_url = self.ui.download_url_input.text()
            self.fetch_ts_info_from_url(m3u8_url, max_retries)
        else:
            self.fetch_ts_info_from_file(max_retries)

    def fetch_ts_info_from_url(self, m3u8_url, max_retries):
        try:
            res = requests.get(m3u8_url, timeout=(3, 5), verify=False, headers=self.headers)
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
                self.fetch_ts_info_from_url(self._m3u8_url, self._max_retries)
            else:
                m3u8_text_str = res.text
                self.fetch_m3u8_ts_url(m3u8_text_str)
        except Exception as e:
            _logger.error('{} error: {}'.format(m3u8_url, e))
            if max_retries > 0:
                self.fetch_ts_info_from_url(m3u8_url, max_retries - 1)

    def fetch_ts_info_from_file(self, max_retries):
        try:
            res_content = open('/home/1di0t/Videos/合并报表2.m3u8', 'r')
            res_content = res_content.read()
            self.fetch_m3u8_ts_url(res_content)
        except Exception as e:
            if max_retries > 0:
                self.fetch_ts_info_from_file(max_retries - 1)

    def get_save_ts_file_folder(self):
        if not self.ui.download_file_path_input.text():
            file_path_name = './{}'.format(self._m3u8_file_name)
        else:
            file_path_name = '{}/{}'.format(self.ui.download_file_path_input.text(), self._m3u8_file_name)
        return file_path_name

    def get_m3u8_ts_merge_mp4_file(self):
        if not self.ui.download_file_path_input.text():
            file_path_name = './{}.mp4'.format(self._m3u8_file_name)
        else:
            file_path_name = '{}/{}.mp4'.format(self.ui.download_file_path_input.text(), self._m3u8_file_name)
        return file_path_name

    def get_new_m3u8_file(self):
        if not self.ui.download_file_path_input.text():
            file_path_name = './{}.m3u8'.format(self._m3u8_file_name)
        else:
            file_path_name = '{}/{}.m3u8'.format(self.ui.download_file_path_input.text(), self._m3u8_file_name)
        return file_path_name

    def fetch_m3u8_ts_url(self, m3u8_text_str):
        """
        fetch ts url
        """
        file_folder = self.get_save_ts_file_folder()
        new_m3u8_file = self.get_new_m3u8_file()
        if not os.path.exists(file_folder):
            os.mkdir(file_folder)
        new_m3u8_str = ''
        ts = compute_sum()
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
                new_m3u8_str += f"{file_folder}/{next(ts)}\n"
                self._m3u8_ts_list.append(line)
            elif re.search(r'^/', line) is not None:
                new_m3u8_str += f"{file_folder}/{next(ts)}\n"
                self._m3u8_ts_list.append(self.front_url + line)
            else:
                new_m3u8_str += f"{file_folder}/{next(ts)}\n"
                self._m3u8_ts_list.append(self._m3u8_url.rsplit("/", 1)[0] + '/' + line)
        self.ts_sum = next(ts)
        with open(f"{new_m3u8_file}", "w") as f:
            f.write(new_m3u8_str)

    def get_ts_key_file_name_with_path(self):
        if not self.ui.download_file_path_input.text():
            file_path_name = './{}/key'.format(self._m3u8_file_name)
        else:
            file_path_name = '{}/{}/key'.format(self.ui.download_file_path_input.text(), self._m3u8_file_name)
        return file_path_name

    def download_key(self, key_line, num_retries):
        """
        下载key文件
        """
        key_file_path = self.get_ts_key_file_name_with_path()
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
            with open(key_file_path, 'wb') as f:
                f.write(res.content)
            res.close()
            return f'{key_line.split(mid_part)[0]}URI="{key_file_path}"{key_line.split(mid_part)[-1]}'
        except Exception as e:
            _logger.error('error: {}'.format(e))
            if os.path.exists(key_file_path):
                os.remove(key_file_path)
            if num_retries > 0:
                self.download_key(key_line, num_retries - 1)

    def set_download_table_view(self):
        for index_ts, ts_line in enumerate(self._m3u8_ts_list):
            self.model_table_list.appendRow(
                [QStandardItem(index_ts),
                 QStandardItem(ts_line),
                 QStandardItem('未下载')]
            )

    def set_download_list_view(self, list_item):
        list_model = QStringListModel()
        list_model.setStringList(list_item)
        self.download_file_list.setModel(list_model)

    def update_download_process_property(self, value):
        if not self._m3u8_ts_list:
            self.ui.download_progress.setValue(0)
        else:
            process_value = math.ceil((value / len(self._m3u8_ts_list)) * 100)
            self.ui.download_progress.setValue(process_value)

    async def save_resp_content_to_file(self, resp, ts_file_obj):
        while True:
            chunk_file = await resp.content.read(self._chunk_size)
            if not chunk_file:
                break
            ts_file_obj.write(chunk_file)

    async def _m3u8_download_ts(self, ts_url, save_ts_name, max_retry):
        file_path_name = self.get_ts_file_name_with_path(save_ts_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(ts_url) as resp:
                if resp.status == 200:
                    with open(file_path_name, "wb") as ts:
                        await self.save_resp_content_to_file(resp, ts)

                    self.success_sum += 1
                    self.update_download_process_property(self.success_sum)
                else:
                    await self._m3u8_download_ts(ts_url, save_ts_name, max_retry - 1)
                resp.close()

    def get_ts_file_name_with_path(self, save_ts_name):
        if not self.ui.download_file_path_input.text():
            file_path_name = './{}/{}'.format(self._m3u8_file_name, save_ts_name)
        else:
            file_path_name = '{}/{}/{}'.format(self.ui.download_file_path_input.text(), self._m3u8_file_name,
                                               save_ts_name)
        return file_path_name

    async def m3u8_download_ts(self, ts_url, save_ts_name, max_retry):
        try:
            file_path_name = self.get_ts_file_name_with_path(save_ts_name)
            ts_url = ts_url.split('\n')[0]
            if not os.path.exists(file_path_name):
                await self._m3u8_download_ts(ts_url, save_ts_name, max_retry)
            else:
                self.success_sum += 1
                self.update_download_process_property(self.success_sum)
            return ts_url
        except Exception as e:
            _logger.error('{}, error: {}'.format(ts_url, e))
            file_path_name = self.get_ts_file_name_with_path(save_ts_name)
            if os.path.exists(file_path_name):
                os.remove(file_path_name)
            if max_retry > 0:
                await self.m3u8_download_ts(ts_url, save_ts_name, max_retry - 1)
            return e

    def initial_page(self):
        self.ui.show()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    download_app = QApplication(sys.argv)
    # loop = QEventLoop(download_app)
    # asyncio.set_event_loop(loop)

    download_windows = DownloadM3U8QtUI()
    download_windows.ui.show()
    download_windows.ui.download_url_input.setText('https://s3.fsvod1.com/20220225/aoYBKlCA/index.m3u8')
    download_windows.ui.download_file_name_input.setText('测试')
    download_windows.ui.download_file_path_input.setText('/home/jx/Videos/测试')
    # while loop:
    #     loop.run_forever()
    download_app.exec_()
