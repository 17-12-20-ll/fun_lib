import os
import time
import requests
import hashlib
from random import Random

import qrcode


APP_ID = ""  # 公众账号appid
MCH_ID = ""  # 商户号
API_KEY = ""  # 微信商户平台(pay.weixin.qq.com) -->账户设置 -->API安全 -->密钥设置，设置完成后把密钥复制到这里
UFDODER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # url是微信下单api
NOTIFY_URL = "http://xxx/get_pay/callback/"  # 微信支付结果回调接口,需要你自定义
CREATE_IP = '111.111.11.11'  # 你服务器上的ip


def random_str(randomlength=8):
    """
    生成随机字符串
    :param randomlength: 字符串长度
    :return:
    """
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKbkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()

    print("randomlength : ", randomlength)

    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    print('str:', str)
    return str


def order_num(phone):
    """
    生成扫码付款订单号
    :param phone: 手机号
    :return:
    """
    local_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    result = phone + 'T' + local_time + random_str(5)
    return result


def get_sign(data_dict, key):
    # 签名函数，参数为签名的数据和密钥
    params_list = sorted(data_dict.items(), key=lambda e: e[0], reverse=False)  # 参数字典倒排序为列表
    params_str = "&".join(u"{}={}".format(k, v) for k, v in params_list) + '&key=' + key
    # 组织参数字符串并在末尾添加商户交易密钥
    md5 = hashlib.md5()  # 使用MD5加密模式
    md5.update(params_str.encode('utf-8'))  # 将参数字符串传入
    sign = md5.hexdigest().upper()  # 完成加密并转为大写
    return sign


def trans_dict_to_xml(data_dict):  # 定义字典转XML的函数
    data_xml = []
    for k in sorted(data_dict.keys()):  # 遍历字典排序后的key
        v = data_dict.get(k)  # 取出字典中key对应的value
        if k == 'detail' and not v.startswith('<![CDATA['):  # 添加XML标记
            v = '<![CDATA[{}]]>'.format(v)
        data_xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(data_xml)).encode('utf-8')  # 返回XML，并转成utf-8，解决中文的问题


def trans_xml_to_dict(data_xml):
    soup = BeautifulSoup(data_xml, features='xml')
    xml = soup.find('xml')  # 解析XML
    if not xml:
        return {}
    data_dict = dict([(item.name, item.text) for item in xml.find_all()])
    return data_dict


def wx_pay_unifiedorde(detail):
    """
    访问微信支付统一下单接口
    :param detail:
    :return:
    """
    detail['sign'] = get_sign(detail, API_KEY)
    xml = trans_dict_to_xml(detail)  # 转换字典为XML
    response = requests.request('post', UFDODER_URL, data=xml)  # 以POST方式向微信公众平台服务器发起请求
    return response.content


def pay_fail(err_msg):
    """
    微信支付失败
    :param err_msg: 失败原因
    :return:
    """
    data_dict = {'return_msg': err_msg, 'return_code': 'FAIL'}
    return trans_dict_to_xml(data_dict)


def create_qrcode(username, url):
    """
    生成扫码支付二维码
    :param username: 用户名
    :param url: 支付路由
    :return:
    """
    get_path = "%s/%s" % (settings.MEDIA_ROOT, "QRcode")  # 创建文件夹路径
    img_path = "%s/%s" % (settings.MEDIA_ROOT, "QRcode/")  # 创建文件路径

    img = qrcode.make(url)  # 创建支付二维码片
    # 你存放二维码的地址 uploads/media
    img_url = img_path + username + '.png'  # 创建文件

    if not os.path.exists(get_path):
        os.makedirs(get_path)
    img.save(img_url)

    ret_url = settings.MEDIA_URL + 'QRcode/' + username + '.png'  # 前端展示路径

    return ret_url
