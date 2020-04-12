import re
import time
import uuid

from django.http import HttpResponse

from user.models import User
from utils.alipay_pkg.gen_qrcode import pay
from utils.alipay_pkg.pay_class import *

from django.db import connection
from django.views.decorators.csrf import csrf_exempt

from trade.models import TradeType, CardRechargeList, Invoice, Order
from utils.export_excel import export
from utils.manage_resp import resp
from utils.manage_token import check_token

# ============交易数据展示==============
from utils.tools import gen_order_id, encode_order, decode_order, parsing_data
from utils.wexin_pkg.pay import wxpay, get_qr_code, Wxpay_Result, trans_dict_to_xml


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


def get_trade_type_all_name(request):
    """用于卡密充值，获取所有的充值类型"""
    if request.method == 'GET':
        t_all = TradeType.objects.all()
        return resp(data=[i.to_name_dict() for i in t_all])


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
        if pwd_num < 6 or pwd_num > 12:
            return resp(201, '长度错误')
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


@csrf_exempt
def update_card(request):
    """编辑卡密"""
    if request.method == 'POST':
        c_id = request.POST.get('id')
        t = request.POST.get('trade_type_id')
        card_id = request.POST.get('card_id')
        card_pwd = request.POST.get('card_pwd')
        c = CardRechargeList.objects.filter(id=c_id).first()
        c.trade_type_id = t
        c.card_id = card_id
        c.card_pwd = card_pwd
        c.save()
        return resp()


def format_trade_card_list(data):
    t = TradeType.objects.filter(id=data[4]).first()
    return {
        'id': data[0],
        'card_id': data[1],
        'card_pwd': data[2],
        'is_use': data[3],
        'trade_type': t.name,
        'group': t.group.name,
    }


def get_card(request):
    """
    查询所有
    条件查询
    分页查寻
    :param request:
    :return:
    """
    if request.method == 'GET':
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        tmp_d = [i for i in d if d[i]]
        if len(tmp_d) > 2:
            # 查询时 group_id=1&login_name=u&user_name=k&email=1096
            tmp_l = []
            for i in d:
                if i not in ['p', 'n']:
                    if d[i]:
                        if i == 'card':
                            tmp_l.append(f'card_id like "%{d[i]}%"')
                        elif i == 't':
                            tmp_l.append(f'trade_type_id={d[i]}')
            tmp_sql = ' and '.join(tmp_l)
            # 代表有检索条件
            sql = f'select id,card_id,card_pwd,is_use,trade_type_id from card_recharge_list where {tmp_sql}' \
                  f' order by id desc limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select id,card_id,card_pwd,is_use,trade_type_id from card_recharge_list' \
                  f' order by id desc limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        data = [format_trade_card_list(i) for i in cursor.fetchall()]
        sql = re.sub(r'id,card_id.*?trade_type_id', 'count(*)', sql)
        sql = sql.split("limit")[0].strip()
        cursor.execute(sql)
        l = cursor.fetchone()
        cursor.close()
        return resp(data=data, count=l[0])


def export_card(request):
    if request.method == 'GET':
        """导出可用数据到excel中"""
        c = ['卡号', '卡密', '所属资源']
        c_l = CardRechargeList.objects.filter(is_use=0).all()
        datas = [i.export_list() for i in c_l]
        # 重新定位到开始
        opt = export(c, datas)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=卡密.xls'
        response.write(opt)
        return response


def format_order_export_list(d):
    tmp_type = {
        1: '支付宝在线支付',
        2: '微信在线支付',
        3: '卡密充值'
    }
    return [d[1], tmp_type[d[2]], d[3], d[5], d[6], d[7].strftime("%Y-%m-%d %H:%M:%S"), d[8]]


def export_financial_manager_excel(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        start = request.GET.get('s')
        end = request.GET.get('e')
        # 查询数据库的对应数据进行数据导出
        sql = f'select * from `order`  where add_time >= "{start}" and add_time <= "{end} 23:59:59"'
        cursor.execute(sql)
        data = [format_order_export_list(i) for i in cursor.fetchall()]
        cols = ["用户名", '充值类型', '卡号', '总价', '天数', '充值时间', '线程数']
        opt = export(cols, data)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=卡密.xls'
        response.write(opt)
        return response


# ============交易行为==============


def get_order_status(request):
    if request.method == 'GET':
        """查询订单状态 """
        o_id = request.GET.get('order_id')
        o = Order.objects.filter(id=o_id).first()
        if o:
            # 代表已经支付
            return resp(200, '已支付')
        return resp(202, '未支付')


@csrf_exempt
def card_recharge(request):
    """卡号充值"""
    if request.method == 'POST':
        # 清除字符串两边空格
        card_id = request.POST.get('card_id')
        card_pwd = request.POST.get('card_pwd')
        if card_id and card_pwd:
            card_id = card_id.strip()
            card_pwd = card_pwd.strip()
        else:
            return resp(205, '参数不正确')
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
        # 获取当前用户是否过期，如果用户存在会员并且没有过期，产生升级、续费的操作。
        if u.group_id != 1 and u.end_time > datetime.datetime.now():
            # 当前用户存在会员并且没有过期
            # 获取到交易类型分辨vip等级
            u_trade_type = u.group.t.all()[0]
            re_name = re.findall(r'(VI.*?\d)', u_trade_type.name)[0]
            if re_name in c.trade_type.name:
                # 当前会员进行续费,续费也可以是对月、年续费
                return resp(300, '是否续费当前会员')
            else:
                # 当前用户进行升级
                return resp(301, '是否升级会员')
        # 过期时间 = 支付订单时间 + 过期天数
        u.end_time = datetime.datetime.now() + datetime.timedelta(days=c.trade_type.days)
        u.group = c.trade_type.group
        u.save()
        c.is_use = 1
        c.save()
        # 创建订单
        o = Order()
        o.id = encode_order(str(time.time()))
        o.login_name = u.login_name
        o.trade_type = 3
        o.card_id = card_id
        o.trade_group = c.trade_type_id
        o.days = c.trade_type.days
        o.total = float(c.trade_type.price)
        o.desc = '1'
        o.save()
        return resp()


@csrf_exempt
def public_transfer(request):
    """对公转账"""
    if request.method == 'POST':
        # 该项记录由管理员进行添加财务信息，添加后，改变用户的权限
        login_name = request.POST.get('login_name')
        # 获取当前用户
        u = User.objects.filter(login_name=login_name).first()
        if not u:
            return resp(400, '没有该用户')
        trade_type_id = request.POST.get('trade_type')
        enable = int(request.POST.get('enable'))
        # 直接获取当前交易类型的用户分组，获取分组、获取交易天数、交易价格。
        t = TradeType.objects.filter(id=trade_type_id).first()
        g = t.group
        d = t.days
        p = t.price
        m_type = 4  # 对公转账
        o = Order()
        o.id = encode_order(f'{login_name}{g}{d}{p}')
        o.login_name = login_name
        o.trade_type = m_type
        o.trade_group = g.id
        o.total = p
        o.days = d
        o.desc = 1
        o.save()
        # 改变用户行为
        u.group = g
        u.enable = enable
        u.end_time = datetime.datetime.now() + datetime.timedelta(days=d)
        u.save()
        return resp()


# 交易思路：1. 通过页面获取充值信息，充值成功-> 添加一条记录到财务管理中， 此时修改用户的分组，以及到期时间

def get_ratio(cur):
    """获取比率"""
    # 获取当前交易分类的名字
    cur_name = cur.name
    # 查询当前分组中的包含数据以VIP进行数据捕获
    re_name = re.findall(r'(VI.*?\d)', cur_name)
    if re_name:
        # 捕获到VIP数据字段
        re_name = re_name[0]
        if "月" in cur_name:
            # 当前为月 就获取年份的
            t_all = TradeType.objects.filter(name__contains=re_name)
            for i in t_all:
                if i.name != cur_name:
                    return i.price / cur.price
        else:
            # 当前为年，就获取月份的
            t_all = TradeType.objects.filter(name__contains=re_name)
            for i in t_all:
                if i.name != cur_name:
                    return cur.price / i.price


@csrf_exempt
def get_pay_new_qr_code(request):
    """采用简单化的订单管理，将所有信息使用base64进行加密，存入订单id中"""
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        if not obj:
            return resp(201, '用户过期')
        u_id = obj['id']
        trade_group_type = request.POST.get('trade_group_type')
        t = TradeType.objects.filter(pk=trade_group_type).first()
        # 总价
        sum_price = float(request.POST.get('sum_price'))
        # 只能使用 1 2
        pay_type = int(request.POST.get('pay_type'))
        # 并发数
        concurrent = request.POST.get('concurrent')
        # 是否升级参数
        up = request.POST.get('up')  # True or False
        # 保存所有信息到订单id中，为了避免订单表中生成多余的没有成立的订单
        # 生成订单参数,需要存入支付方式(pay_type),并发线程(concurrent),用户id(u_id),支付的等级(trade_group_type)
        order_id = encode_order(gen_order_id(u_id, pay_type, trade_group_type, concurrent))
        # 获取二维码之前，判断用户是否据有会员、过期时间等。如果有--升级操作，如果没有--购买操作，升级需要提示。
        u = User.objects.filter(id=u_id).first()
        if u.group_id > 1 and u.end_time > datetime.datetime.now() and (not up):
            # 当前存在会员，采用升级操作,返回当前用户到期时间和当前所属等级，折算时间
            # 判断重新选择的数据分组是否和上一次一样、如果一样的话，直接进行续费
            u_trade_type = u.group.t.all()[0]
            # 判断选择的分组日期，不允许使用月份进行对应年份
            if u_trade_type == t:
                return resp(301, '是否续费')
            tmp_name_1 = t.name.split('会员')
            tmp_name_2 = u_trade_type.name.split('会员')
            if tmp_name_1[0] == tmp_name_2[0]:
                if "月" in tmp_name_1[1]:
                    return resp(310, '月份暂不支持续费')
                elif "年" in tmp_name_1[1]:
                    return resp(301, '是否续费')
            # 由于包月与包年暂时没有关系，此处使用价格进行关联
            # 转换率是xx会员包月与当前xx会员包年的比率
            t_price = t.price * get_ratio(t) if t.days == 31 else t.price
            u_price = u_trade_type.price * get_ratio(u_trade_type) if u_trade_type.days == 31 else u_trade_type.price
            y_days = (u.end_time - datetime.datetime.now()).days
            u_unit_price = u_price / 366
            t_unit_price = t_price / 366
            y_price = y_days * u_unit_price
            n_days = y_price / t_unit_price
            data = {
                'name': u.group.name,
                'end_time': u.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                'cur': t.name,
                'y_days': int(n_days)
            }
            return resp(300, '是否升级', data=data)
        if pay_type == 1:
            alipay = Alipay()
            # 订单5min过期
            payer = pay(out_trade_no=order_id, total_amount=sum_price, subject="开心图书馆", timeout_express='5m',
                        alipay=alipay)
            ret = alipay.trade_pre_create(out_trade_no=payer.out_trade_no, total_amount=payer.total_amount,
                                          subject=payer.subject, timeout_express=payer.timeout_express)
            return resp(data=payer.get_qr_code(ret['qr_code']), order_id=order_id)
        elif pay_type == 2:
            ret = wxpay(out_trade_no=order_id, subject='开心图书馆', total_amount=sum_price)  # total_amount单位为分
            return resp(data=get_qr_code(ret['code_url']), order_id=order_id)
        return resp(400, '访问出错')


# ========================= 支付回调 =============
def save_order(out_trade_no, total):
    data = parsing_data(decode_order(out_trade_no))
    u = User.objects.filter(id=data['u_id']).first()
    login_name = u.login_name
    t = TradeType.objects.filter(id=data['trade_group_type']).first()
    # 添加订单
    o = Order()
    o.id = out_trade_no
    o.login_name = login_name
    o.trade_type = data['pay_type']
    o.trade_group = data['trade_group_type']
    o.total = total
    o.days = t.days
    o.desc = data['concurrent']
    o.add_time = datetime.datetime.now()
    o.save()
    u = User.objects.filter(login_name=login_name).first()
    u.enable = int(data['concurrent'])
    # 判断当前用户所属分组，如果不是未付费会员、并且没有到过期时间。则该操作是一个升级或者续费的操作
    if u.group_id > 1 and u.end_time > datetime.datetime.now():
        u_trade_type = u.group.t.all()[0]
        t_price = t.price * 11 if t.days == 31 else t.price
        u_price = u_trade_type.price * 11 if u_trade_type.days == 31 else u_trade_type.price
        y_days = (u.end_time - datetime.datetime.now()).days
        u_unit_price = u_price / 366
        t_unit_price = t_price / 366
        y_price = y_days * u_unit_price
        n_days = y_price / t_unit_price
        # 升级或者续费，都是进行一个当前时间 + 余下时间 + 订单购买时间
        u.end_time = datetime.datetime.now() + datetime.timedelta(days=n_days) + datetime.timedelta(days=o.days)
    else:
        # 过期时间 = 支付订单时间 + 过期天数
        u.end_time = o.add_time + datetime.timedelta(days=o.days)
    u.group = TradeType.objects.filter(id=o.trade_group).first().group
    u.save()


@csrf_exempt
def pay_return(request):
    if request.method == 'POST':
        trade_status = request.POST.get('trade_status')
        if trade_status:
            # 支付宝支付
            if trade_status == 'TRADE_SUCCESS':
                out_trade_no = request.POST.get('out_trade_no')
                total = request.POST.get('total_amount')
                save_order(out_trade_no, total)
                return resp(msg='支付成功')
            else:
                return resp(1001, '支付错误')
        else:
            # 微信支付
            wechat_result = Wxpay_Result()
            result = wechat_result.post(request)
            if result['result_code'] == 'SUCCESS':
                # 请求成功数据回调
                out_trade_no = result['out_trade_no']
                total = float(int(result['total_fee']) * 100)
                save_order(out_trade_no, total)
                return HttpResponse(trans_dict_to_xml({'return_code': 'SUCCESS', 'return_msg': 'OK'}))
            else:
                return HttpResponse(trans_dict_to_xml({'return_code': 'FAIL', 'return_msg': 'SIGNERROR'}))
    if request.method == "GET":
        return resp()
