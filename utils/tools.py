import base64
import json
import time

import requests

from utils.manage_token import encrypt, decrypt


def timestamp_to_str(timestamp=None, format='%Y-%m-%d %H:%M:%S'):
    """
    :param timestamp: 当前时间戳
    :param format: 格式化时间样式
    :return: 返回2020-02-13 23:53:39样式
    """
    if timestamp:
        return time.strftime(format, time.localtime(timestamp))
    else:
        return time.strftime(format, time.localtime())


# 下述两个方法适用于任何地方的字符串加解密
def img_code_overdue_create(**kwargs):
    """构建验证码序列"""
    return encrypt(kwargs)


a = 'ZXlKZmRHbHRaU0k2SWpFMU9ESXpOVEF3TmpBaUxDSjJZV3dpT2pJM0xDSmxlQ0k2TXpBd2ZROjFqNU5YRjpVS3JEOHpsZWtJdlJsaG9Ud1duc1dGN3hJSXc'


def img_code_overdue_decode(token):
    """解析图片验证码的对象"""
    obj = decrypt(token)
    if int(obj['_time']) + obj['ex'] <= time.time():
        return False
    return obj


def del_pos(l: list):
    tmp = sorted(l, key=lambda x: x['pos'])
    for i in tmp:
        del i['pos']
    return tmp


def splash_execute():
    splash_url = "http://47.104.73.6:8080/execute"
    data = {
        'images': '0',
        'timeout': '90',
        'url': 'http://login.elib.tcd.ie/login',
        "lua_source": """function main(splash, args)
            splash:set_user_agent("Mozilla/5.0  Chrome/69.0.3497.100 Safari/537.36")
            splash:go(args.url)
            splash:wait(1)
            splash:select("input[name='user']"):send_text("gleesoev")
            splash:select("input[name='pass']"):send_text("Drumcondra8")
            splash:wait(5)
            local button = splash:select("input[name='Submit2']")
            local bounds = button:bounds()
            button:mouse_click{x=bounds.width/3, y=bounds.height/3}
            splash:wait(10)
            return {
                url = splash:url(),
                cookies = splash:get_cookies(),
            }
        end"""
    }
    for _ in range(3):
        try:
            response = requests.post(splash_url, json=data)
            return response.json()["cookies"]
        except Exception as e:
            print(e)


def string_encryption(cookies):
    """把字符串加密"""
    while True:
        if type(cookies) is list:
            str_encrypt = json.dumps(cookies)
            cookies = str()
        base64_encrypt = str(base64.b64encode(
            str_encrypt.encode('utf-8')), 'utf-8')
        if "=" not in base64_encrypt:
            return base64_encrypt[::-1]
        str_encrypt = base64_encrypt[:]


def gen_order_id(u_id, pay_type, trade_group_type, concurrent, flag=int(time.time())):
    return f'{u_id}|{pay_type}|{trade_group_type}|{concurrent}|{flag}'


def encode_order(data):
    """把字符串加密"""
    base64_encrypt = str(base64.b64encode(
        data.encode('utf-8')), 'utf-8')
    return base64_encrypt


def decode_order(data):
    """解密"""
    return str(base64.b64decode(data.encode('utf-8')), 'utf-8')


def parsing_data(data):
    """解析订单id数据"""
    tmp = data.split('|')
    return {
        'u_id': tmp[0],
        'pay_type': int(tmp[1]),
        'trade_group_type': int(tmp[2]),
        'concurrent': tmp[3]
    }


def parsing_list(data):
    """解析嵌套列表为简单列表"""
    while 1:
        b = []
        num = 1
        for i in data:
            if isinstance(i, list):  # 检测含有可迭代类型，则将i中子元素添加到b，相当于去掉一个[]
                num = 0
                for j in i:
                    b.append(j)
            else:
                b.append(i)
        data = b  # 赋值给a，继续检测是否含有可迭代类型
        if num:  # 逐一检测a，若num=1，标明a中没有可迭代类型，完成检测
            break
    return set(b)


if __name__ == '__main__':
    print(img_code_overdue_decode(a))
