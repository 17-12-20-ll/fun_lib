import requests
from utils.wexin_pkg.config import *
from django.views import View


def wxpay(out_trade_no, subject, total_amount):
    nonce_str = random_str()  # 拼接出随机的字符串即可，我这里是用 时间+随机数字+5个随机字母
    total_fee = 1  # 付款金额，单位是分，必须是整数
    print('total_amount:', total_amount)
    params = {
        'appid': APP_ID,  # APPID
        'mch_id': MCH_ID,  # 商户号
        'nonce_str': nonce_str,  # 随机字符串
        'out_trade_no': out_trade_no,  # 订单编号，可自定义
        'total_fee': int(total_fee),  # 订单总金额
        'spbill_create_ip': CREATE_IP,  # 自己服务器的IP地址
        'notify_url': NOTIFY_URL,  # 回调地址，微信支付成功后会回调这个url，告知商户支付结果
        'body': subject,  # 商品描述
        # 'detail': '马杀鸡'.encode('utf-8'),  # 商品描述
        'trade_type': 'NATIVE',  # 扫码支付类型
    }
    sign = get_sign(params, API_KEY)  # 获取签名
    params['sign'] = sign  # 添加签名到参数字典
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    response = requests.post(UFDODER_URL, data=xml.encode('utf-8'))  # 以POST方式向微信公众平台服务器发起请求
    return trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典


def wxpay_query(out_trade_no):
    nonce_str = random_str()  # 拼接出随机的字符串即可，我这里是用 时间+随机数字+5个随机字母
    params = {
        'appid': APP_ID,  # APPID
        'mch_id': MCH_ID,  # 商户号
        'nonce_str': nonce_str,  # 随机字符串
        'out_trade_no': out_trade_no,  # 订单编号，可自定义
        # 'detail': '马杀鸡'.encode('utf-8'),  # 商品描述
    }
    sign = get_sign(params, API_KEY)  # 获取签名
    params['sign'] = sign  # 添加签名到参数字典
    xml = trans_dict_to_xml(params)  # 转换字典为XML
    response = requests.post(QUERY_URL, data=xml.encode('utf-8'))  # 以POST方式向微信公众平台服务器发起请求
    data_dict = trans_xml_to_dict(response.content)  # 将请求返回的数据转为字典
    if data_dict['trade_state'] == 'SUCCESS':
        return True
    else:
        return False


class Wxpay_Result(View):
    """
    微信支付结果回调通知路由
    """

    def post(self, request, *args, **kwargs):
        """
        微信支付成功后会自动回调
        返回参数为：
        {'mch_id': '',
        'time_end': '',
        'nonce_str': '',
        'out_trade_no': '',
        'trade_type': '',
        'openid': '',
         'return_code': '',
         'sign': '',
         'bank_type': '',
         'appid': '',
         'transaction_id': '',
         'cash_fee': '',
         'total_fee': '',
         'fee_type': '', '
         is_subscribe': '',
         'result_code': 'SUCCESS'}
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data_dict = trans_xml_to_dict(request.body)  # 回调数据转字典
        # print('支付回调结果', data_dict)
        sign = data_dict.pop('sign')  # 取出签名
        back_sign = get_sign(data_dict, API_KEY)  # 计算签名
        # 验证签名是否与回调签名相同
        if sign == back_sign and data_dict['return_code'] == 'SUCCESS':
            '''
            检查对应业务数据的状态，判断该通知是否已经处理过，如果没有处理过再进行处理，如果处理过直接返回结果成功。
            '''
            # 处理支付成功逻辑
            # 返回接收结果给微信，否则微信会每隔8分钟发送post请求
            return data_dict
        return False


if __name__ == '__main__':
    print(wxpay('1245346', '开心图书馆', 1))
    print(wxpay_query('1245346'))
# {'return_code': 'SUCCESS', 'return_msg': 'OK', 'appid': 'wx7b9d0eb255b24e3b', 'mch_id': '1577556781', 'nonce_str': 'puBnqLFpY3HnOebt', 'sign': '296D17958C9A2DCA028FF761AF1DB576', 'result_code': 'SUCCESS', 'openid': 'oROPr5oTD7l9hcINzmtglVXIntQs', 'is_subscribe': 'N', 'trade_type': 'NATIVE', 'bank_type': 'OTHERS', 'total_fee': '1', 'fee_type': 'CNY', 'transaction_id': '4200000518202002286882552024', 'out_trade_no': '40bc25e1edb338e4a9985d43f2ee496c', 'attach': ' ', 'time_end': '20200228171342', 'trade_state': 'SUCCESS', 'cash_fee': '1', 'trade_state_desc': '支付成功', 'cash_fee_type': 'CNY'}
