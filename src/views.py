import json
import re

import demjson
from django.db import connection
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from src.models import OneSrc, TwoSrc, OneSrcGroup, FourSrc, ThreeSrc
from trade.models import CardRechargeList, TradeType
from user.models import User, Group
from utils.manage_resp import resp

# ===================OneSrc=====================
from utils.manage_token import check_token
from utils.send_email import send_mail
from utils.tools import del_pos, splash_execute, string_encryption, parsing_list


def get_one_src_info(request):
    """查询一级分类资源"""
    if request.method == 'GET':
        s_id = request.GET.get('id')
        if s_id:
            """返回单条数据"""
            s = OneSrc.objects.filter(id=s_id).first()
            return resp(data=s.to_detail_dict() if s else 'not src')
        else:
            """返回所有数据"""
            s_all = OneSrc.objects.all()
            return resp(data=[i.to_list_dict() for i in s_all])


def format_one_src_list(data):
    return {
        'id': data[0],
        'name': data[1],
        'pos': data[2]
    }


def get_one_src(request):
    cursor = connection.cursor()
    d = request.GET
    p = int(d.get('p', 1))
    n = int(d.get('n', 10))
    tmp_d = [i for i in d if d[i]]
    if len(tmp_d) > 2:
        # name
        # 代表有检索条件
        sql = f'select id,name,pos from one_src where name like "%{d["name"]}%" limit {(p - 1) * n},{n}'
    else:
        # 代表查询所有数据分页
        sql = f'select id,name,pos from one_src order by id desc limit {(p - 1) * n},{n}'
    cursor.execute(sql)
    data = [format_one_src_list(i) for i in cursor.fetchall()]
    sql = re.sub(r'id,.*?pos', 'count(*)', sql)
    sql = sql.split("limit")[0].strip()
    cursor.execute(sql)
    l = cursor.fetchone()
    cursor.close()
    return resp(data=data, count=l[0])


@csrf_exempt
def add_one_src(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        groups = json.loads(request.POST.get('groups'))
        o_src = OneSrc()
        o_src.name = name
        o_src.desc = desc
        o_src.pos = pos
        o_src.save()
        OneSrcGroup.objects.bulk_create([OneSrcGroup(group_id=i, one_src_id=o_src.id) for i in groups])
        return resp()


@csrf_exempt
def update_one_src(request):
    if request.method == 'POST':
        o_id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        groups = json.loads(request.POST.get('groups'))  # 数组
        o = OneSrc.objects.filter(id=o_id).first()
        o.name = name
        o.desc = desc
        o.pos = pos
        o.save()
        # 获取之前
        o_groups = [i.group_id for i in o.og.all()]
        # 删除的集合
        del_set = set(o_groups) - set(groups)
        # 新增的集合
        add_set = set(groups) - set(o_groups)
        # 修改分组
        # 删除
        if del_set:
            OneSrcGroup.objects.filter(group_id__in=del_set).delete()
        # 新增
        if add_set:
            OneSrcGroup.objects.bulk_create([OneSrcGroup(group_id=i, one_src_id=o.id) for i in add_set])
        return resp()


def get_to_name_one_src(request):
    """根据一级资源名称获取数据"""
    if request.method == 'GET':
        name = request.GET.get('name')
        o_s = OneSrc.objects.all()
        if name:
            o_s = OneSrc.objects.filter(name__contains=name)
        return resp(data=[i.to_list_dict() for i in o_s])


# ===================TwoSrc=====================
@csrf_exempt
def add_two_src(request):
    if request.method == 'POST':
        src_type = request.POST.get('src_type')
        one_src_id = request.POST.get('one_src')
        name = request.POST.get('name')
        title_url = request.POST.get('title_url')
        pos = request.POST.get('pos')
        content = request.POST.get('content')
        t_src = TwoSrc()
        t_src.src_type = int(src_type)
        t_src.one_src_id = int(one_src_id)
        t_src.name = name
        t_src.title_url = title_url
        t_src.pos = int(pos)
        t_src.content = content
        t_src.save()
        return resp()


@csrf_exempt
def update_two_src(request):
    """更新二级资源"""
    if request.method == 'POST':
        t_id = request.POST.get('id')
        name = request.POST.get('name')
        title_url = request.POST.get('title_url')
        content = request.POST.get('content')
        pos = int(request.POST.get('pos'))
        src_type = int(request.POST.get('src_type') if request.POST.get('src_type') else 1)
        one_src = int(request.POST.get('one_src_id'))
        t = TwoSrc.objects.filter(id=t_id).first()
        t.name = name
        t.title_url = title_url
        t.content = content
        t.pos = pos
        t.src_type = src_type
        t.one_src_id = one_src
        t.save()
        return resp(data=t.to_update_return())


def get_two_src_info(request):
    if request.method == 'GET':
        t_id = request.GET.get('id')
        if t_id:
            t = TwoSrc.objects.filter(id=t_id).first()
            return resp(data=t.to_detail_dict() if t else 'not src')
        else:
            t_all = TwoSrc.objects.all()
            return resp(data=[i.to_name_id_dict() for i in t_all])


def get_front_src_info(request):
    if request.method == 'GET':
        s_all = OneSrc.objects.all()
        return resp(data=del_pos([i.to_all_dict() for i in s_all]))


def format_two_src_list(data):
    return {'id': data[0], 'one_name': data[1], 'two_name': data[2], 'pos': data[3],
            'add_time': data[4].strftime("%Y/%m/%d %H:%M:%S")}


def get_two_src_page_count(request):
    """获取二级资源的总页数"""
    if request.method == 'GET':
        count = TwoSrc.objects.count()
        return resp(count=count)


def get_two_src_page_data(request):
    """二级资源分页处理"""
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        cursor.execute(f'select a.id,b.name,a.name,a.pos,a.add_time from two_src a join one_src b on b.id=a.one_src_id'
                       f' limit {(page - 1) * page_num},{page_num}')
        cursor.close()
        return resp(data=[format_two_src_list(i) for i in cursor.fetchall()])


# ==============改写分页数据
def get_two_src(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        tmp_d = [i for i in d if d[i]]
        if len(tmp_d) > 2:
            # 查询时 有一级分类，标题
            # 一级分类为 one_src_id
            tmp_l = []
            for i in d:
                if i not in ['p', 'n']:
                    if d[i]:
                        if i == 'one_src_id':
                            tmp_l.append(f'a.one_src_id={d[i]}')
                        if i == 'name':
                            tmp_l.append(f'a.name like "%{d[i]}%"')
            tmp_sql = ' and '.join(tmp_l)
            # 代表有检索条件
            sql = f'select a.id,b.name,a.name,a.pos,a.add_time from two_src a join one_src b on b.id=a.one_src_id' \
                  f' where {tmp_sql} order by a.id desc limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select a.id,b.name,a.name,a.pos,a.add_time from two_src a join one_src b on b.id=a.one_src_id' \
                  f' order by a.id desc limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        data = [format_two_src_list(i) for i in cursor.fetchall()]
        sql = re.sub(r'a\.id,.*?add_time', 'count(*)', sql)
        sql = sql.split("limit")[0].strip()
        cursor.execute(sql)
        l = cursor.fetchone()
        cursor.close()
        return resp(data=data, count=l[0])


# ===================ThreeSrc=====================

def format_three_src_list(data):
    """格式化资源入口数据"""
    return {
        'id': data[0],
        'name': data[1],
        'pos': data[2],
        'url': data[3],
        'add_time': data[4].strftime("%Y-%m-%d %H:%M:%S"),
        'two_src_name': data[5],
        'four_src_name': data[6]
    }


def get_three_src_page_data(request):
    """三级资源数据"""
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        cursor.execute(
            f'select a.id,a.name,a.pos,a.url,a.add_time,b.name,c.name from three_src a join two_src b on'
            f' a.two_src_id=b.id join four_src c on a.four_src_id=c.id'
            f' limit {(page - 1) * page_num},{page_num}')
        cursor.close()
        data = [format_three_src_list(i) for i in cursor.fetchall()]
        return resp(data=data, count=len(data))


def get_three_src_page_count(request):
    """获取三级资源总数"""
    if request.method == 'GET':
        count = ThreeSrc.objects.count()
        return resp(count=count)


# 获取三级分页数据
def get_three_src(request):
    if request.method == 'GET':
        # 获取筛选条件数据
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        tmp_d = [i for i in d if d[i]]
        if len(tmp_d) > 2:
            # 查询时 有二级资源名称、三级资源名称、四级资源名称
            tmp_l = []
            for i in d:
                if i not in ['p', 'n']:
                    if d[i]:
                        if i == 'tw':  # two
                            tmp_l.append(f'b.name like "%{d[i]}%"')
                        elif i == 'th':  # three
                            tmp_l.append(f'a.name like "%{d[i]}%"')
                        elif i == 'fo':  # four
                            tmp_l.append(f'c.name like "%{d[i]}%"')
            tmp_sql = ' and '.join(tmp_l)
            # 代表有检索条件
            sql = f'select a.id,a.name,a.pos,a.url,a.add_time,b.name,c.name from three_src a join two_src b on ' \
                  f'b.id=a.two_src_id join four_src c on ' \
                  f'c.id=a.four_src_id where {tmp_sql} order by a.id desc limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select a.id,a.name,a.pos,a.url,a.add_time,b.name,c.name from three_src a join two_src b on ' \
                  f'b.id=a.two_src_id join four_src c on ' \
                  f'c.id=a.four_src_id order by a.id desc limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        data = [format_three_src_list(i) for i in cursor.fetchall()]
        sql = re.sub(r'a\.id,.*?c.name', 'count(*)', sql)
        sql = sql.split("limit")[0].strip()
        cursor.execute(sql)
        l = cursor.fetchone()
        cursor.close()
        return resp(data=data, count=l[0])


@csrf_exempt
def add_three_src(request):
    """添加三级资源"""
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        url = request.POST.get('url')
        two_src_id = request.POST.get('two_src')
        four_src_id = request.POST.get('four_src')
        tr_src = ThreeSrc()
        tr_src.name = name
        tr_src.desc = desc
        tr_src.pos = pos
        tr_src.url = url
        tr_src.two_src_id = two_src_id
        tr_src.four_src_id = four_src_id
        tr_src.save()
        return resp()


@csrf_exempt
def update_three_src(request):
    """修改三级资源"""
    if request.method == 'POST':
        t_id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        url = request.POST.get('url')
        two_src_id = request.POST.get('two_src')
        four_src_id = request.POST.get('four_src')
        tr_src = ThreeSrc.objects.filter(id=t_id).first()
        tr_src.name = name
        tr_src.desc = desc
        tr_src.pos = pos
        tr_src.url = url
        tr_src.two_src_id = two_src_id
        tr_src.four_src_id = four_src_id
        tr_src.save()
        return resp()


def get_three_src_info(request):
    """获取三级资源"""
    if request.method == 'GET':
        tr_id = request.GET.get('id')
        t = request.GET.get('t')  # 查询或者是编辑的获取详情
        if tr_id:
            tr = ThreeSrc.objects.filter(id=tr_id).first()
            return resp(data=tr.to_simple_back_dict() if t == 'edit' else tr.to_simple_dict() if tr else 'not src')
        else:
            tr_all = ThreeSrc.objects.all()
            return resp(data=[i.to_simple_dict() for i in tr_all])


# ===================FourSrc=====================
@csrf_exempt
def add_four_src(request):
    """添加四级资源"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        url = request.POST.get('url')
        success_url = request.POST.get('success_url')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        code_script = request.POST.get('code_script')
        cookie_time = int(request.POST.get('cookie_time')) if request.POST.get('cookie_time') else 0
        # json.loads 正常解析'{"x":1, "y":2, "z":3}'
        # 但不能解析 "{x:1, y:2, z:3}"
        # 借助demjson.decode解析
        try:
            cookie = demjson.decode(request.POST.get('cookie')) if request.POST.get('cookie') else ''
        except:
            # 如果存储的是字符串，就不会被json解析。
            cookie = request.POST.get('cookie')
        error_field = request.POST.get('error_field')
        f = FourSrc()
        f.name = name
        f.code = code
        f.url = url
        f.desc = desc
        f.username = username
        f.pwd = pwd
        f.code_script = code_script
        f.cookie_time = cookie_time
        f.cookie = cookie
        f.success_url = success_url
        f.error_field = error_field
        f.save()
        return resp()


@csrf_exempt
def update_four_src(request):
    """编辑账号资源"""
    if request.method == "POST":
        f_id = request.POST.get('id')
        name = request.POST.get('name')
        url = request.POST.get('url')
        code = request.POST.get('code')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        code_script = request.POST.get('code_script')
        cookie_time = int(request.POST.get('cookie_time'))
        cookie = demjson.decode(request.POST.get('cookie'))
        success_url = request.POST.get('success_url')
        error_field = request.POST.get('error_field')
        f = FourSrc.objects.filter(id=f_id).first()
        f.name = name
        f.code = code
        f.url = url
        f.desc = desc
        f.username = username
        f.pwd = pwd
        f.code_script = code_script
        f.cookie_time = cookie_time
        f.cookie = cookie
        f.success_url = success_url
        f.error_field = error_field
        f.save()
        return resp(data=f.to_detail_dict())


def get_four_src_info(request):
    if request.method == 'GET':
        f_id = request.GET.get('id')
        if f_id:
            f = FourSrc.objects.filter(id=f_id).first()
            return resp(data=f.to_detail_dict() if f else 'not src')
        else:
            f_all = FourSrc.objects.all()
            return resp(data=[i.to_name_dict() for i in f_all])


def format_four_src_list(data):
    """格式化账号信息资源"""
    return {
        "id": data[0],
        "name": data[1],
        "code": data[2],
        "url": data[3],
        "username": data[4],
        "pwd": data[5],
        "add_time": data[6].strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_four_src(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        tmp_d = [i for i in d if d[i]]
        if len(tmp_d) > 2:
            # 查询时 标题和编码
            tmp_l = []
            for i in d:
                if i not in ['p', 'n']:
                    if d[i]:
                        if i == 'name':
                            tmp_l.append(f'name like "%{d[i]}%"')
                        if i == 'code':
                            tmp_l.append(f'code like "%{d[i]}%"')
            tmp_sql = ' and '.join(tmp_l)
            # 代表有检索条件
            sql = f'select id,name,code,url,username,pwd,add_time from four_src' \
                  f' where {tmp_sql} order by id desc limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select id,name,code,url,username,pwd,add_time from four_src' \
                  f' order by id desc limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        data = [format_four_src_list(i) for i in cursor.fetchall()]
        sql = re.sub(r'id,.*?add_time', 'count(*)', sql)
        sql = sql.split("limit")[0].strip()
        cursor.execute(sql)
        l = cursor.fetchone()
        cursor.close()
        return resp(data=data, count=l[0])


def query_four_src(request):
    """查询账号资源"""
    if request.method == 'GET':
        d = request.GET
        q = Q()
        for i in d:
            if d[i] and i != "page" and i != "page_num":
                tmp = i + '__contains'
                q.add(Q(**{tmp: d[i]}), Q.AND)
        data = FourSrc.objects.filter(q)
        return resp(data=[i.to_detail_dict() for i in data])


def test(request):
    if request.method == 'GET':
        """测试：数据同步三级资源"""
        return resp(data='success')


# =================== 公共删除接口
def del_data(request):
    if request.method == "GET":
        t = request.GET.get('t')
        obj_id = request.GET.get('id')
        obj = ''
        if t == 'user':
            obj = User.objects.filter(id=obj_id)
        elif t == 'one_src':
            # 进行级联删除 ，删除关于当前一级分类的数据
            obj = OneSrc.objects.filter(id=obj_id)
        elif t == 'two_src':
            obj = TwoSrc.objects.filter(id=obj_id)
        elif t == 'three_src':
            obj = ThreeSrc.objects.filter(id=obj_id)
        elif t == 'four_src':
            obj = FourSrc.objects.filter(id=obj_id)
        elif t == 'group':
            obj = Group.objects.filter(id=obj_id)
        elif t == 'card':
            obj = CardRechargeList.objects.filter(id=obj_id)
        elif t == 'trade_type':
            obj = TradeType.objects.filter(id=obj_id)
        elif t == 'admin':
            obj = User.objects.filter(id=obj_id).filter(is_admin=1)
        if obj:
            # 特殊关系需要处理的数据 一级分类
            if t == 'one_src':
                # 先进行级联关系数据删除
                o = obj.first()
                OneSrcGroup.objects.filter(one_src_id=o.id).delete()
            if t == 'group':
                # 删除会员分组，并带有资源关联的数据。先删除关联数据。
                o = obj.first()
                OneSrcGroup.objects.filter(group_id=o.id).delete()
            obj.delete()
            return resp(msg='删除成功!')
        else:
            return resp(400, '没有查找到该资源')


@csrf_exempt
def get_resource(request):
    if request.method == 'POST':
        # 三级资源id
        t_id = int(request.POST.get("code"))
        token = request.POST.get("token")
        # 1.判断用户token是否有效
        if (not token) or token == 'null':
            return resp(404, '没有token')
        obj = check_token(token)
        if not obj:
            return resp(404, 'token过期')
        u_id = obj['id']
        # 判断
        # 2.判断用户是否有权限访问该资源 ,无访问权限返回404
        u = User.objects.filter(id=u_id).first()
        ids = [i.to_one_dict() for i in u.group.go.all()]
        ids = parsing_list(ids)
        if t_id not in ids:
            return resp(404, '无权限访问')
        # 3.根据三级资源获取cookie数据
        t = ThreeSrc.objects.filter(id=t_id).first()
        cookie = t.four_src.cookie
        # 4.根据三级资源获取登陆链接
        url = t.four_src.url
        return resp(data={
            "href": url,
            "thing": string_encryption(cookie)
        })


# ============ 资源错误回调邮箱
def re_email(request):
    if request.method == 'POST':
        msg = request.POST.get('msg')
        to = request.POST.get('to')
        send_mail(to, msg=msg)
        return resp()
