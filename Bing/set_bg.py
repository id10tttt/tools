# -*- coding: utf-8 -*-
import logging
import os
import random
# gi.require_version('Gtk', '3.0')  # 需要设置要使用的 GNOME 版本
from gi.repository import Gio

_logger = logging.getLogger(__name__)

BACKGROUND_SCHEMA = "org.gnome.desktop.background"
BACKGROUND_KEY = "picture-uri"
BACKGROUND_DARK_KEY = "picture-uri-dark"

BASE_PICTURE_FOLDER = '/home/ylscm/Pictures/Bing/'


class BackgroundWallpaper(object):
    def __init__(self):
        self.bg_settings = Gio.Settings.new(BACKGROUND_SCHEMA)
        self.base_image_folder = BASE_PICTURE_FOLDER
        self.background_key = BACKGROUND_KEY
        self.background_dark_key = BACKGROUND_DARK_KEY

    def get_random_file(self):
        directory = self.base_image_folder
        # 检查目录是否存在
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory '{directory}' not found.")

        # 获取目录中所有文件的列表
        files = os.listdir(directory)

        # 从列表中随机选择一个文件
        random_file = random.choice(files)

        # 构建文件的完整路径
        file_path = os.path.join(directory, random_file)

        return file_path

    def set_background_image(self):
        image_file = self.get_random_file()
        image_file = 'file://{}'.format(image_file)
        _logger.info('开始设置: {}, {}'.format(image_file, dir(self.bg_settings)))
        self.bg_settings[self.background_key] = '{}'.format(image_file)
        self.bg_settings[self.background_dark_key] = '{}'.format(image_file)
        _logger.info('当前壁纸: {}'.format(self.bg_settings[self.background_key]))
        _logger.info('当前壁纸Dark: {}'.format(self.bg_settings[self.background_dark_key]))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    BackgroundWallpaper().set_background_image()
