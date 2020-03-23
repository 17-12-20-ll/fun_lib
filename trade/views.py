import time
import uuid

from user.models import User
from utils.alipay_pkg.gen_qrcode import pay
from utils.alipay_pkg.pay_class import *
import random

from django.db import connection
from django.views.decorators.csrf import csrf_exempt

from trade.models import TradeType, CardRechargeList, Invoice, Order
from utils.manage_resp import resp
from utils.manage_token import check_token


# ============交易数据展示==============
def get_trade_type_info(request):
    if request.method == 'GET':
        t_id = request.GET.get('id')
        t = request.GET.get('t')
        if t_id:
            t = TradeType.objects.filter(id=t_id).first()
            return resp(data=t.to_dict() if t else 'not type')
        else:
            t_all = TradeType.objects.all()
            return resp(data=[i.to_front_dict() if t == 'front' else i.to_dict() for i in t_all])


@csrf_exempt
def update_trade_type(request):
    if request.method == 'POST':
        t_id = request.POST.get('id')
        name = request.POST.get('name')
        price = request.POST.get('price')
        days = request.POST.get('days')
        group = request.POST.get('group')
        t = TradeType.objects.filter(id=t_id).first()
        t.name = name
        t.price = price
        t.days = days
        t.group_id = group
        t.save()
        return resp()


@csrf_exempt
def add_trade_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = int(request.POST.get('price'))
        days = request.POST.get('days')
        group = int(request.POST.get('group'))
        t = TradeType()
        t.name = name
        t.price = price
        t.days = days
        t.group_id = group
        t.save()
        return resp()


def query_trade_type(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        ts = TradeType.objects.filter(name__contains=name)
        return resp(data=[i.to_dict() for i in ts])


# ==================== 发票 ======================
@csrf_exempt
def invoice(request):
    token = request.META.get('HTTP_AUTHENTICATION')
    obj = check_token(token)
    u_id = obj['id']
    if request.method == 'POST':
        company = request.POST.get('company')
        code = request.POST.get('code')
        addr_tel = request.POST.get('addr_tel')
        acount = request.POST.get('acount')
        receive_email = request.POST.get('receive_email')
        receive_user = request.POST.get('receive_user')
        receive_addr = request.POST.get('receive_addr')
        receive_phone = request.POST.get('receive_phone')
        flag = request.POST.get('flag')  # 传递falg :create 代表新建 ，不传值代表修改
        i = Invoice() if flag == 'create' else Invoice.objects.filter(u_id=u_id).first()
        i.u_id = u_id
        i.company = company
        i.code = code
        i.addr_tel = addr_tel
        i.acount = acount
        i.receive_email = receive_email
        i.receive_user = receive_user
        i.receive_addr = receive_addr
        i.receive_phone = receive_phone
        i.save()
        return resp()
    if request.method == 'GET':
        # 确定是否为一对一，一对多，目前采取一对一的形式
        i = Invoice.objects.filter(u_id=u_id).first()
        if i:
            return resp(data=i.to_dict())
        else:
            return resp(400, '没有资源')


@csrf_exempt
def update_invoice(request):
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        u_id = obj['id']
        company = request.POST.get('company')
        code = request.POST.get('code')
        addr_tel = request.POST.get('addr_tel')
        acount = request.POST.get('acount')
        receive_email = request.POST.get('receive_email')
        receive_user = request.POST.get('receive_user')
        receive_addr = request.POST.get('receive_addr')
        receive_phone = request.POST.get('receive_phone')
        i = Invoice.objects.filter(u_id=u_id).first()
        i.company = company
        i.code = code
        i.addr_tel = addr_tel
        i.acount = acount
        i.receive_email = receive_email
        i.receive_user = receive_user
        i.receive_addr = receive_addr
        i.receive_phone = receive_phone
        i.save()
        return resp()


# ======================= 卡密类型===================
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


@csrf_exempt
def add_n_card(request):
    """自动生成n组卡密"""
    if request.method == 'POST':
        trade_type_id = request.POST.get('trade_type_id')
        # 获取需要生成的卡密个数
        num = int(request.POST.get('num'))
        # 获取需要生成的密码位数,密码生成范围在 6-12之间
        pwd_num = int(request.POST.get('pwd_num'))
        # 实现唯一卡密，使用uuid1作为卡号,使用uuid4作为卡密
        CardRechargeList.objects.bulk_create(
            [CardRechargeList(card_id=''.join([i for i in str(uuid.uuid1()) if i != '-']),
                              card_pwd=str(uuid.uuid4()).split('-').pop()[:pwd_num], trade_type_id=trade_type_id) for _
             in range(num)])
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


def format_trade_card_list(data):
    return {
        'id': data[0],
        'card_id': data[1],
        'card_pwd': data[2],
        'is_use': data[3],
        'trade_type': data[4],
        'group': data[5],
    }


def get_card_page_data(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        sql = f'select a.id,a.card_id,a.card_pwd,a.is_use,b.name,c.name from card_recharge_list a join trade_type' \
              f' b on a.trade_type_id=b.id join `group` c on b.group_id=c.id limit {(page - 1) * page_num},{page_num}'
        cursor.execute(sql)
        cursor.close()
        return resp(data=[format_trade_card_list(i) for i in cursor.fetchall()])


def get_card_page_count(request):
    if request.method == 'GET':
        count = CardRechargeList.objects.count()
        return resp(count=count)


# ============交易行为==============
# 交易思路：1. 通过页面获取充值信息，充值成功-> 添加一条记录到财务管理中， 此时修改用户的分组，以及到期时间
@csrf_exempt
def get_pay_qr_code(request):
    """获取交易二维码，创建订单"""
    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        # 需要获取用户token，判断用户是否可以进行操作
        trade_group_type = request.POST.get('trade_group_type')
        # 只能使用 1 2 3
        pay_type = int(request.POST.get('pay_type'))
        # 并发数
        concurrent = int(request.POST.get('concurrent'))
        t = TradeType.objects.filter(id=trade_group_type).first()
        total = t.price * concurrent
        o = Order()
        o.login_name = login_name
        o.trade_type = pay_type
        o.desc = concurrent
        o.trade_group = int(trade_group_type)
        o.total = total
        o.days = t.days
        o.order_end_time = int(time.time()) + 300
        o.save()
        # 订单号
        order_id = o.id
        # 生成订单参数
        alipay = Alipay()
        payer = pay(out_trade_no=order_id, total_amount=total, subject="开心图书馆", timeout_express='5m',
                    alipay=alipay)
        ret = alipay.trade_pre_create(out_trade_no=payer.out_trade_no, total_amount=payer.total_amount,
                                      subject=payer.subject, timeout_express=payer.timeout_express)
        return resp(data=payer.get_qr_code(ret['qr_code']), order_id=order_id)


def get_order_status(request):
    if request.method == 'GET':
        """查询订单状态 """
        o_id = request.GET.get('order_id')
        o = Order.objects.filter(id=o_id).first()
        if o.status == 1:
            # 代表已经支付
            return resp(200, '已支付')
        return resp(202, '未支付')


@csrf_exempt
def card_recharge(request):
    """卡号充值"""
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        card_pwd = request.POST.get('card_pwd')
        # 判断卡号是否存在
        c = CardRechargeList.objects.filter(card_id=card_id).first()
        if not c:
            return resp(202, '资源不存在')
        if c.is_use:
            return resp(201, '资源已被使用')
        if c.card_pwd != card_pwd:
            return resp(203, '密码错误，请联系商家')
        # 通过校验，开始进行充值
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        if not obj:
            return resp(204, '用户信息过期')
        u_id = obj['id']
        u = User.objects.filter(id=u_id).first()
        # 过期时间 = 支付订单时间 + 过期天数
        u.end_time = datetime.datetime.now() + datetime.timedelta(days=c.trade_type.days)
        u.group = c.trade_type.group
        u.save()
        c.is_use = 1
        c.save()
        return resp()


# ========================= 支付回调 =============
@csrf_exempt
def alipay_return(request):
    if request.method == 'POST':
        if request.POST.get('trade_status'):
            trade_status = request.POST.get('trade_status')
            if trade_status == 'TRADE_SUCCESS':
                out_trade_no = request.POST.get('out_trade_no')
                order_obj = Order.objects.filter(id=out_trade_no).first()
                # 修改订单支付状态
                order_obj.status = 1
                order_obj.add_time = datetime.datetime.now()
                order_obj.save()
                # 获取下单用户 login_name
                login_name = order_obj.login_name
                u = User.objects.filter(login_name=login_name).first()
                u.enable = int(order_obj.desc)
                # 过期时间 = 支付订单时间 + 过期天数
                u.end_time = order_obj.add_time + datetime.timedelta(days=order_obj.days)
                u.group = TradeType.objects.filter(id=order_obj.trade_group).first().group
                u.save()
                return resp()
            else:
                return resp(1001, '支付错误')
    if request.method == "GET":
        return resp()
