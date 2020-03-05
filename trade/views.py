from django.views.decorators.csrf import csrf_exempt

from trade.models import TradeType, Invoice
from utils.manage_resp import resp

# ============交易数据展示==============
from utils.manage_token import check_token


def get_trade_type_info(request):
    if request.method == 'GET':
        t_id = request.GET.get('id')
        if t_id:
            t = TradeType.objects.filter(id=t_id).first()
            return resp(data=t.to_dict() if t else 'not type')
        else:
            t_all = TradeType.objects.all()
            return resp(data=[i.to_dict() for i in t_all])


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
