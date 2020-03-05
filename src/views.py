import json

from django.db import connection
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from src.models import OneSrc, TwoSrc, OneSrcGroup, FourSrc
from utils.manage_resp import resp

# ===================OneSrc=====================
from utils.tools import del_pos


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


def get_one_src_page_data(request):
    """获取一级分类的资源"""
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        cursor.execute(f'select id,name,pos from one_src limit {(page - 1) * page_num},{page_num}')
        cursor.close()
        return resp(data=[format_one_src_list(i) for i in cursor.fetchall()])


def get_one_src_page_count(request):
    """获取一级分类的总数"""
    if request.method == 'GET':
        count = OneSrc.objects.count()
        return resp(count=count)


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
        for i in groups:
            # 新添多对多关系
            og = OneSrcGroup()
            og.one_src_id = o_src.id
            og.group_id = i
            og.save()
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
            return resp(data=[i.to_list_dict() for i in t_all])


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


def query_two_src(request):
    """条件查询二级资源"""
    if request.method == 'GET':
        d = request.GET
        q = Q()
        for i in d:
            if d[i] and i != "page" and i != "page_num":
                tmp = i if i == 'one_src_id' else i + '__contains'
                q.add(Q(**{tmp: d[i]}), Q.AND)
        data = TwoSrc.objects.filter(q)
        return resp(data=[i.to_update_return() for i in data])


# ===================ThreeSrc=====================
def get_three_src_page_data(request):
    """三级资源数据"""
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        cursor.execute(f'select a.id,b.name,a.name,a.pos,a.add_time from two_src a join one_src b on b.id=a.one_src_id'
                       f' limit {(page - 1) * page_num},{page_num}')
        cursor.close()


# ===================FourSrc=====================
@csrf_exempt
def add_four_src(request):
    """添加四级资源"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        f = FourSrc()
        f.name = name
        f.code = code
        f.desc = desc
        f.username = username
        f.pwd = pwd
        f.save()
        return resp()


@csrf_exempt
def update_four_src(request):
    """编辑账号资源"""
    if request.method == "POST":
        f_id = request.POST.get('id')
        name = request.POST.get('name')
        code = request.POST.get('code')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        f = FourSrc.objects.filter(id=f_id).first()
        f.name = name
        f.code = code
        f.desc = desc
        f.username = username
        f.pwd = pwd
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
            return resp(data=[i.to_list_dict() for i in f_all])


def format_four_src_list(data):
    """格式化账号信息资源"""
    return {
        "id": data[0],
        "name": data[1],
        "code": data[2],
        "username": data[3],
        "pwd": data[4],
        "add_time": data[5].strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_four_src_page_data(request):
    """获取账号密码资源分页数据"""
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        cursor.execute(
            f'select id,name,code,username,pwd,add_time from four_src limit {(page - 1) * page_num},{page_num}')
        cursor.close()
        return resp(data=[format_four_src_list(i) for i in cursor.fetchall()])


def get_four_src_page_count(request):
    """获取二级资源的总页数"""
    if request.method == 'GET':
        count = FourSrc.objects.count()
        return resp(count=count)


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
