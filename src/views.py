import json

from django.views.decorators.csrf import csrf_exempt

from src.models import OneSrc, TwoSrc, OneSrcGroup, ThreeSrc, FourSrc
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


# ===================TwoSrc=====================
@csrf_exempt
def add_two_src(request):
    if request.method == 'POST':
        src_type = request.POST.get('src_type')
        one_src_id = request.POST.get('one_src_id')
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


# ===================ThreeSrc=====================
def insert(request):
    return resp()


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


def get_four_src_info(request):
    if request.method == 'GET':
        f_id = request.GET.get('id')
        if f_id:
            f = FourSrc.objects.filter(id=f_id).first()
            return resp(data=f.to_detail_dict() if f else 'not src')
        else:
            f_all = FourSrc.objects.all()
            return resp(data=[i.to_list_dict() for i in f_all])
