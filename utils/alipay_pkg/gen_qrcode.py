from utils.alipay_pkg.pay_class import *
import qrcode, time
from io import BytesIO
import base64


class pay:
    def __init__(self, out_trade_no, total_amount, subject, timeout_express, alipay):
        self.out_trade_no = out_trade_no
        self.total_amount = total_amount
        self.subject = subject
        self.timeout_express = timeout_express
        self.alipay = alipay

    def get_qr_code(self, code_url):
        '''
        生成二维码
        :return None
        '''
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1
        )
        qr.add_data(code_url)  # 二维码所含信息
        img = qr.make_image()  # 生成二维码图片
        jpeg_image_buffer = BytesIO()
        img.save(jpeg_image_buffer, format='JPEG')
        base64_str = base64.b64encode(jpeg_image_buffer.getvalue()).decode()
        return base64_str
        # img.save('qr_test_ali.png')
        # print('二维码保存成功！')

    def query_order(self, out_trade_no: int):
        '''
        :param out_trade_no: 商户订单号
        :return: Nonem
        '''
        try:
            _time = 0
            for i in range(300):
                time.sleep(1)
                result = self.alipay.init_alipay_cfg().api_alipay_trade_query(out_trade_no=out_trade_no)
                if result.get("trade_status", "") == "TRADE_SUCCESS":
                    print('订单已支付!')
                    return True
                _time += 2
                # print('订单查询返回值：', result)
            return False
        except:
            print('订单超时')
            return False


if __name__ == '__main__':
    alipay = Alipay()
    payer = pay(out_trade_no="45666a", total_amount=0.01, subject="开心图书馆", timeout_express='5m',
                alipay=alipay)
    dict = alipay.trade_pre_create(out_trade_no=payer.out_trade_no, total_amount=payer.total_amount,
                                   subject=payer.subject, timeout_express=payer.timeout_express)
    print(payer.get_qr_code(dict['qr_code']))
    pass
