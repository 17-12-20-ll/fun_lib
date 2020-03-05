import time

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


if __name__ == '__main__':
    print(img_code_overdue_decode(a))
