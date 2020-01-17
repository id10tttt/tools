#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 中国节日
CHINESE_FESTIVAL = {
    1: {
        1: '元旦节',
        8: '周总理逝世悼念日'
    },
    2: {
        14: '情人节'
    },
    3: {
        5: '中国青年志愿者服务日',
        8: '国际劳动妇女节',
        12: '中国植树节',
        15: '消费者权益保护日',
        16: '手拉手情系贫困小伙伴全国统一行动日',
        18: '全国科技人才活动日'
    },
    4: {
        1: '国际愚人节',
        5: '清明节',
        15: '全民国家安全教育日',
        23: '中国海军建军节',
        24: '中国航天日',
        25: '全国预防接种宣传日',
        30: '全国交通安全反思日'
    },
    5: {
        1: '国际劳动节',
        4: '中国青年节'
    },
    6: {
        1: '国际儿童节',
        5: '世界环境日',
        6: '全国爱眼日'
    },
    7: {
        1: '中国共产党诞生日',
        7: '中国人民抗日战争纪念日1937'
    },
    8: {
        1: '中国人民解放军建军节',
        15: '第二次世界大战对日本抗战胜利纪念日'
    },
    9: {
        3: '中国抗日战争胜利纪念日',
        10: '中国教师节',
        18: '九·一八事变纪念日(中国国耻日)',
        21: '国际和平日'
    },
    10: {
        1: '国庆节',
        31: '万圣节'
    },
    11: {
        9: '中国消防宣传日(消防节)'
    },
    12: {
        1: '世界艾滋病日',
        12: '西安事变纪念日',
        13: '南京大屠杀纪念日',
        24: '平安夜',
        25: '圣诞节'
    }
}

# 农历月份
LUNAR_MONTH = {
    '正月': 1,
    '二月': 2,
    '三月': 3,
    '四月': 4,
    '五月': 5,
    '六月': 6,
    '七月': 7,
    '八月': 8,
    '九月': 9,
    '十月': 10,
    '十一月': 11,
    '十二月': 12
}

# 月份
MON_ENG = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

# 星期
WEK_ENG = {
    '星期一': 'Monday',
    '星期二': 'Tuesday',
    '星期三': 'Wednesday',
    '星期四': 'Thursday',
    '星期五': 'Friday',
    '星期六': 'Saturday',
    '星期日': 'Sunday',
}

# 闰
LEAP_MONTH = '閏'

# 天干
TIAN_GAN_DATA = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DI_ZHI_DATA = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 生肖
ZODIAC = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

ZHI_ZODIAC = {
    x[0]: x[1] for x in zip(DI_ZHI_DATA, ZODIAC)
}