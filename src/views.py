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


@csrf_exempt
def update_one_src(request):
    """修改一级资源"""
    if request.method == 'POST':
        id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        groups = json.loads(request.POST.get('groups'))
        o_src = OneSrc.objects.filter(id=id).first()
        o_src.name = name
        o_src.desc = desc
        o_src.pos = pos
        o_src.save()
        o_groups = [i.group_id for i in o_src.og.all()]
        """删除的数据"""
        del_group = set(o_groups) - set(groups)
        """新增的数据"""
        add_group = set(groups) - set(o_groups)
        if del_group:
            OneSrcGroup.objects.filter(group_id__in=del_group).delete()
        if add_group:
            OneSrcGroup.objects.bulk_create([OneSrcGroup(group_id=i, one_src_id=id) for i in add_group])
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


@csrf_exempt
def update_two_src(request):
    """修改二级资源"""
    if request.method == 'POST':
        id = request.POST.get('id')
        src_type = request.POST.get('src_type')
        one_src_id = request.POST.get('one_src_id')
        name = request.POST.get('name')
        title_url = request.POST.get('title_url')
        pos = request.POST.get('pos')
        content = request.POST.get('content')
        t_src = TwoSrc.objects.filter(id=id).first()
        t_src.src_type = src_type
        t_src.one_src_id = one_src_id
        t_src.name = name
        t_src.title_url = title_url
        t_src.pos = pos
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


@csrf_exempt
def add_three_src(request):
    """添加三级资源"""
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        url = request.POST.get('url')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        username_field = request.POST.get('username_field')
        pwd_field = request.POST.get('pwd_field')
        two_src_id = request.POST.get('two_src_id')
        four_src_id = request.POST.get('four_src_id')
        tr_src = ThreeSrc()
        tr_src.name = name
        tr_src.desc = desc
        tr_src.pos = pos
        tr_src.url = url
        tr_src.username = username
        tr_src.pwd = pwd
        tr_src.username_field = username_field
        tr_src.pwd_field = pwd_field
        tr_src.two_src_id = two_src_id
        tr_src.four_src_id = four_src_id
        tr_src.save()
        return resp()


@csrf_exempt
def update_three_src(request):
    """修改三级资源"""
    if request.method == 'POST':
        id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        pos = request.POST.get('pos')
        url = request.POST.get('url')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        username_field = request.POST.get('username_field')
        pwd_field = request.POST.get('pwd_field')
        two_src_id = request.POST.get('two_src_id')
        four_src_id = request.POST.get('four_src_id')
        tr_src = ThreeSrc.objects.filter(id=id).first()
        tr_src.name = name
        tr_src.desc = desc
        tr_src.pos = pos
        tr_src.url = url
        tr_src.username = username
        tr_src.pwd = pwd
        tr_src.username_field = username_field
        tr_src.pwd_field = pwd_field
        tr_src.two_src_id = two_src_id
        tr_src.four_src_id = four_src_id
        tr_src.save()
        return resp()


def get_three_src_info(request):
    """获取三级资源"""
    if request.method == 'GET':
        tr_id = request.POST.get('id')
        if tr_id:
            tr = ThreeSrc.objects.filter(id=tr_id).first()
            return resp(data=tr.to_simple_dict() if tr else 'not src')
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
