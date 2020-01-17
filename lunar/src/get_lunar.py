#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from concurrent.futures import ThreadPoolExecutor
import os
import json
import zlib
import base64
import redis

try:
    from ..config.config import CHINESE_FESTIVAL, TIAN_GAN_DATA, DI_ZHI_DATA, ZODIAC, ZHI_ZODIAC
except:
    from lunar.config.config import CHINESE_FESTIVAL, TIAN_GAN_DATA, DI_ZHI_DATA, ZODIAC, ZHI_ZODIAC

start_year = 1901
end_year = 2100

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'

HEADERS = {'User-Agent': user_agent}
BASE_URL = 'https://www.hko.gov.hk/tc/gts/time/calendar/text/files/T{year_number}c.txt'
ZIP_JSON_KEY = 'base64(zip(o))'

records_dict = {}
data_path = '../data/'

redis_client = redis.Redis(db=2)


def download_file(index_year):
    file_name = str(index_year) + '.txt'
    os.chdir(data_path)
    if os.path.exists(data_path + file_name):
        with open(data_path + file_name, 'r') as f_r:
            file_values = f_r.read()
            format_data_to_json(index_year, file_values)
    else:
        dl_url = BASE_URL.format(year_number=index_year)
        req = requests.get(dl_url, headers=HEADERS)
        decode_type = req.apparent_encoding

        decode_values = req.content.decode(decode_type)

        with open(data_path + file_name, 'w') as f_w:
            f_w.write(decode_values)
            f_w.close()
        format_data_to_json(index_year, decode_values)


def get_china_festival(mon_date, day_date):
    if int(mon_date) in CHINESE_FESTIVAL.keys():
        if int(day_date) in CHINESE_FESTIVAL[int(mon_date)].keys():
            return CHINESE_FESTIVAL[int(mon_date)].get(int(day_date))
        else:
            return False
    else:
        return False


def format_data_to_json(index_year, values):
    global records_dict
    # 分行
    values = values.split('\n')

    tmp = {}
    for x in values[3:]:
        line_data = x.split(' ')
        line_data = [cell_data for cell_data in line_data if cell_data]
        if not line_data:
            continue

        # 年月日
        year_mon_day = line_data[0]

        # 农历
        lunar_date = line_data[1]

        # 星期
        week_date = line_data[2]

        # 24节气
        festival_24_date = line_data[3] if len(line_data) > 3 else ''

        # 年月日
        year_date, mon_day_date = year_mon_day.split('年')
        mon_date, day_date = mon_day_date.split('月')

        day_date = day_date.replace('日', '')

        # 获取节日
        festival_china = get_china_festival(mon_date, day_date)

        festival_date = [festival_24_date, festival_china] if festival_china else [festival_24_date]

        day_dict = {
            day_date: {
                'lunar': lunar_date,
                'week': week_date,
                'festival': festival_date
            }
        }
        if mon_date in tmp.keys():
            tmp[mon_date].update(day_dict)
        else:
            tmp[mon_date] = day_dict
    print(tmp)
    year_tian_gan = get_tian_gan_value(index_year)
    print('year_tian_gan', year_tian_gan)
    year_di_zhi = get_di_zhi_value(index_year)
    print('year_di_zhi', year_di_zhi)
    year_zodiac = get_zodiac_value(year_di_zhi)
    print('year_zodiac', year_zodiac)
    records_dict[index_year] = {
        'data': tmp,
        'tian_gan': year_tian_gan,
        'di_zhi': year_di_zhi,
        'zodiac': year_zodiac
    }

    redis_client.hset(index_year, 'data', json.dumps(tmp))
    redis_client.hset(index_year, 'tian_gan', year_tian_gan)
    redis_client.hset(index_year, 'di_zhi', year_di_zhi)
    redis_client.hset(index_year, 'zodiac', year_zodiac)


# 天干
def get_tian_gan_value(year_value):
    gan_year = (year_value - 3) % 10
    return TIAN_GAN_DATA[gan_year - 1]


# 地支
def get_di_zhi_value(year_value):
    zhi_year = (year_value + 7) % 12
    return DI_ZHI_DATA[zhi_year - 1]


def get_gan_zhi_value(year_value, month_value, day_value):
    """
        a = Y mod 80
        b = (5a + [a/4]) mod 60
        c = 10 + [C/4] - C (格里历), c = 8 (儒略历)
        d = (M + 1) mod 2 x 30 + [0.6(M + 1) - 3] - i
        M = 13或14时平年i = -5, 闰年i = -6 (详见下表)
        e = D
        f = (b + c + d + e) mod 60
        g = f mod 10, z = f mod 12
    """
    a = year_value % 80
    b = (5 * a + [a / 4]) % 60
    c = 8


# 生肖
def get_zodiac_value(di_zhi_value):
    return ZHI_ZODIAC[di_zhi_value]


# 压缩
def json_zip(records_dict):
    records_dict = {
        ZIP_JSON_KEY: base64.b64encode(
            zlib.compress(
                json.dumps(records_dict).encode('utf-8')
            )
        ).decode('ascii')
    }
    return records_dict


# 解压
def json_unzip(records_dict, insist=True):
    try:
        assert (records_dict[ZIP_JSON_KEY])
        assert (set(records_dict.keys()) == {ZIP_JSON_KEY})
    except:
        if insist:
            raise RuntimeError("JSON not in the expected format {" + str(ZIP_JSON_KEY) + ": zipstring}")
        else:
            return records_dict

    try:
        records_dict = zlib.decompress(base64.b64decode(records_dict[ZIP_JSON_KEY]))
    except:
        raise RuntimeError("Could not decode/unzip the contents")

    try:
        records_dict = json.loads(records_dict)
    except:
        raise RuntimeError("Could interpret the unzipped contents")

    return records_dict


def main():
    global records_dict
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(download_file, range(start_year, end_year + 1))

    # 压缩
    records_dict = json_zip(records_dict)
    os.chdir(data_path)
    with open(data_path + 'lunar_file.zip', 'w') as f:
        f.write(json.dumps(records_dict))
        f.close()


if __name__ == '__main__':
    main()

    # 解压
    with open(data_path + 'lunar_file.zip', 'r') as f:
        values = json_unzip(json.loads(f.read()))

    for year_key in values.keys():
        for month_key in values[year_key]['data']:
            for day_key in values[year_key]['data'][month_key]:
                print('{} {} {}, {} {} {}'.format(
                    year_key, month_key, day_key, values[year_key]['tian_gan'], values[year_key]['di_zhi'], values[year_key]['zodiac']
                ), values[year_key]['data'][month_key][day_key])
