from django.views.decorators.csrf import csrf_exempt

from trade.models import TradeType
from utils.manage_resp import resp


# ============交易数据展示==============
def get_trade_type_info(request):
    if request.method == 'GET':
        t_id = request.GET.get('id')
        if t_id:
            t = TradeType.objects.filter(id=t_id).first()
            return resp(data=t.to_dict() if t else 'not type')
        else:
            t_all = TradeType.objects.all()
            return resp(data=[i.to_dict() for i in t_all])


# ============交易行为==============
@csrf_exempt
def get_pay_qr_code(request):
    """获取交易二维码，创建订单"""
    if request.method == 'POST':
        # 需要获取用户token，判断用户是否可以进行操作
        trade_group_type = request.POST.get('trade_group_type')
        pay_type = request.POST.get('pay_type')
        # 并发数
        concurrent = int(request.POST.get('concurrent'))
        t = TradeType.objects.filter(id=trade_group_type).first()
        # 模拟订单号
        order_id = '20200222150938_18427_73_1'
        data = {
            'order_id': order_id,
            'total': concurrent * t.price,
            'pay_type': pay_type,
            'qr_code': 'qr_code'
        }
        return resp(data=data)
