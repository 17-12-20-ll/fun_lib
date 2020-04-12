import re

from django.db import connection
from django.views.decorators.csrf import csrf_exempt

from operation.models import HelpClass, HelpList, AdminLoginLog
from utils.manage_resp import resp


@csrf_exempt
def add_help_class(request):
    """增加帮助分类列表"""
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        h_class = HelpClass()
        h_class.name = name
        h_class.desc = desc
        h_class.pos = pos
        h_class.save()
        return resp()


@csrf_exempt
def update_help_class(request):
    """修改帮助分类列表"""
    if request.method == 'POST':
        id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        h_class = HelpClass.objects.filter(id=id).first()
        h_class.name = name
        h_class.desc = desc
        h_class.pos = pos
        h_class.save()
        return resp()


def get_help_class_info(request):
    """获取帮助分类列表信息"""
    if request.method == 'GET':
        h_class_id = request.GET.get('id')
        if h_class_id:
            h_class = HelpClass.objects.filter(id=h_class_id).first()
            return resp(data=h_class.to_detail_dict() if h_class else 'not data')
        else:
            h_class_all = HelpClass.objects.all()
            return resp(data=[i.to_list_dict() for i in h_class_all])


@csrf_exempt
def add_help_list(request):
    """增加帮助列表"""
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        help_class_id = request.POST.get('help_class_id')
        h_list = HelpList()
        h_list.name = name
        h_list.desc = desc
        h_list.pos = pos
        h_list.help_class_id = help_class_id
        h_list.save()
        return resp()


@csrf_exempt
def update_help_list(request):
    """修改帮助列表"""
    if request.method == 'POST':
        id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        help_class_id = request.POST.get('help_class_id')
        h_list = HelpList.objects.filter(id=id).first()
        h_list.name = name
        h_list.desc = desc
        h_list.pos = pos
        h_list.help_class_id = help_class_id
        h_list.save()
        return resp()


def get_help_list_info(request):
    """获取帮助列表信息"""
    if request.method == 'GET':
        h_list_id = request.GET.get('id')
        if h_list_id:
            h_list = HelpList.objects.filter(id=h_list_id).first()
            return resp(data=h_list.to_detail_dict() if h_list else 'not data')
        else:
            h_list_all = HelpList.objects.all()
            return resp(data=[i.to_list_dict() for i in h_list_all])


def format_admin_log_list(data):
    return {
        'name': data[0],
        'time': data[1].strftime("%Y-%m-%d %H:%M:%S"),
        'ip': data[2]
    }


# 管理员登陆日志
def get_admin_log_data(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        sql = f'select admin_name,login_time,login_ip from admin_login_log order by login_time desc limit {(page - 1) * page_num},{page_num}'
        cursor.execute(sql)
        cursor.close()
        return resp(data=[format_admin_log_list(i) for i in cursor.fetchall()])


def get_admin_log_count(request):
    if request.method == 'GET':
        count = AdminLoginLog.objects.count()
        return resp(count=count)


# ================= 用户财务管理
def format_order_list(d):
    # 会员	类型	充值卡号	充值金额	有效期	购买时间	备注
    #  id| login_name | trade_type | card_id| trade_group | total | days | add_time  | desc
    tmp_type = {
        1: '支付宝在线支付',
        2: '微信在线支付',
        3: '卡密充值',
        4: '对公转账'
    }
    return {
        'name': d[1],
        'type': tmp_type[d[2]],
        'card': d[3],
        'total': d[5],
        'days': d[6],
        'time': d[7].strftime("%Y-%m-%d %H:%M:%S"),
        'desc': d[8]
    }


def get_order(request):
    """获取订单数据"""
    if request.method == "GET":
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        tmp_d = [i for i in d if d[i]]
        if len(tmp_d) > 2:
            # 查询时 充值卡号、会员名称
            tmp_l = []
            for i in d:
                if i not in ['p', 'n']:
                    if d[i]:
                        if i == 'card':
                            tmp_l.append(f'card_id="{d[i]}"')
                        if i == 'name':
                            tmp_l.append(f'login_name like "%{d[i]}%"')
            tmp_sql = ' and '.join(tmp_l)
            # 代表有检索条件
            sql = f'select * from `order` where {tmp_sql} limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select * from `order` limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        data = [format_order_list(i) for i in cursor.fetchall()]
        sql = re.sub(r'\*', 'count(*)', sql)
        sql = sql.split("limit")[0].strip()
        cursor.execute(sql)
        l = cursor.fetchone()
        cursor.close()
        return resp(data=data, count=l[0])
