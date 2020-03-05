import random

from django.views.decorators.csrf import csrf_exempt

from trade.models import TradeType, CardRechargeList
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


@csrf_exempt
def add_card(request):
    """手动添加一组卡密"""
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card_pwd = request.POST.get('card_pwd')
        trade_type_id = request.POST.get('trade_type_id')
        c_re = CardRechargeList()
        c_re.card_id = card_id
        c_re.card_pwd = card_pwd
        c_re.trade_type_id = trade_type_id
        c_re.save()
        return resp()


def create_card_id(card_num, card_count):
    dict1 = {5: 10000, 6: 100000, 7: 1000000, 8: 10000000}
    for i in range(5, 10):
        if int(card_num) == i:
            card_id = random.sample(range(int(dict1[i]), int(9 * dict1[i])), int(card_count))
            return card_id


@csrf_exempt
def add_n_card(request):
    """自动生成n组卡密"""
    if request.method == 'POST':
        trade_type_id = request.POST.get('trade_type_id')
        card_count = request.POST.get('card_count')
        card_num = request.POST.get('card_num')
        card_id = create_card_id(card_num, card_count)
        card_pwd = random.sample(range(100000, 999999), int(card_count))
        CardRechargeList.objects.bulk_create([CardRechargeList(card_id=card_id[i], card_pwd=card_pwd[i],
                            trade_type_id=trade_type_id) for i in range(int(card_count))])
        return resp()


def get_card_info(request):
    """查看卡密信息"""
    if request.method == 'GET':
        id = request.GET.get('id')
        if id:
            c = CardRechargeList.objects.filter(id=id).first()
            return resp(data=c.to_dict() if c else 'not card')
        else:
            c_all = CardRechargeList.objects.all()
            return resp(data=[i.to_dict() for i in c_all])