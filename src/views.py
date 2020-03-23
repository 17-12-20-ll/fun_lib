import json

from django.db import connection
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from src.models import OneSrc, TwoSrc, OneSrcGroup, FourSrc, ThreeSrc
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


# ================ 优化分页数据 -- 将搜索和分页集成到一起数目也一起返回
# def create_sql(_source, conditions, **kwargs):
#     """
#     生成对应表的sql语句
#     :param _source: 返回的字段
#     :param conditions: 数据集
#     :param kwargs: 可选值为：groups:分组 orders:排序 table1,table2,table3... 多个表的关联
#     :return: sql语句
#     """
#     # a = f'select id,name,pos from one_src limit {(page - 1) * page_num},{page_num}'
#     _source = ['id', 'name', 'pos']
#     conditions = {'p': 1, 'n': 10}
#     table1 = 'one_src'


def get_one_src(request):
    cursor = connection.cursor()
    d = request.GET
    p = int(d.get('p', 1))
    n = int(d.get('n', 10))
    if len(d) > 2:
        # name
        # 代表有检索条件
        sql = f'select id,name,pos from one_src where name like "%{d["name"]}%" limit {(p - 1) * n},{n}'
    else:
        # 代表查询所有数据分页
        sql = f'select id,name,pos from one_src limit {(p - 1) * n},{n}'
    cursor.execute(sql)
    cursor.close()
    data = [format_one_src_list(i) for i in cursor.fetchall()]
    return resp(data=data, count=len(data))


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


# ==============改写分页数据
def get_two_src(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        if len(d) > 2:
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
                  f' where {tmp_sql} limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select a.id,b.name,a.name,a.pos,a.add_time from two_src a join one_src b on b.id=a.one_src_id' \
                  f' limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        cursor.close()
        data = [format_two_src_list(i) for i in cursor.fetchall()]
        return resp(data=data, count=len(data))


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
        url = request.POST.get('url')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        f = FourSrc()
        f.name = name
        f.code = code
        f.url = url
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
        url = request.POST.get('url')
        code = request.POST.get('code')
        desc = request.POST.get('desc')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        f = FourSrc.objects.filter(id=f_id).first()
        f.name = name
        f.code = code
        f.url = url
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


def get_four_src_page_data(request):
    """获取账号密码资源分页数据"""
    if request.method == 'GET':
        cursor = connection.cursor()
        page = int(request.GET.get('p', 1))
        page_num = int(request.GET.get('n', 10))
        cursor.execute(
            f'select id,name,code,url,username,pwd,add_time from four_src limit {(page - 1) * page_num},{page_num}')
        cursor.close()
        return resp(data=[format_four_src_list(i) for i in cursor.fetchall()])


def get_four_src_page_count(request):
    """获取二级资源的总页数"""
    if request.method == 'GET':
        count = FourSrc.objects.count()
        return resp(count=count)


def get_four_src(request):
    if request.method == 'GET':
        cursor = connection.cursor()
        d = request.GET
        p = int(d.get('p', 1))
        n = int(d.get('n', 10))
        if len(d) > 2:
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
                  f' where {tmp_sql} limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select id,name,code,url,username,pwd,add_time from four_src' \
                  f' limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        cursor.close()
        data = [format_four_src_list(i) for i in cursor.fetchall()]
        return resp(data=data, count=len(data))


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
        # d = [{'name': '090177', 'pwd': '090177'}, {'name': 'goodel13', 'pwd': 'Werttrew1'},
        #      {'name': 'quee2435', 'pwd': 'Oxford2020'}, {'name': 'hwaj', 'pwd': 'Password1'},
        #      {'name': 'nguyet10', 'pwd': '07D5ebd77a1!'}, {'name': 'njmr', 'pwd': 'Mary2466'},
        #      {'name': '05897', 'pwd': 'shonglifen50'}, {'name': '0016186019', 'pwd': 'zxy19860727'},
        #      {'name': '9120150126', 'pwd': 'xly881002'}, {'name': '2010100104', 'pwd': '010034'},
        #      {'name': '20070225', 'pwd': '19800815'}, {'name': 'ncal1', 'pwd': 'April18th'},
        #      {'name': 'test', 'pwd': ''},
        #      {'name': '05092', 'pwd': '19741218'}, {'name': 'SWE1609023', 'pwd': 'SDss123456'},
        #      {'name': 'amijares', 'pwd': 'Pikaplup12301999'}, {'name': '2004990006', 'pwd': 'zys711026'},
        #      {'name': 'b1022976', 'pwd': 'NR2h7b23Ry47'}, {'name': '1406183161', 'pwd': 'hy19831003'},
        #      {'name': 'blank1ls', 'pwd': 'Bridge*0206'}, {'name': '17623', 'pwd': 'Lee'},
        #      {'name': 'lexi.fredericksen@coyotes.usd.edu', 'pwd': 'Lmf1234!'},
        #      {'name': 'snayemi', 'pwd': 'Omar12252014'},
        #      {'name': 'DMP15102', 'pwd': 'Tuckerlove98'}]
        # FourSrc.objects.bulk_create([FourSrc(username=i['name'], pwd=i['pwd']) for i in d])
        # 将三级资源使用账号资源归类
        # t_all = ThreeSrc.objects.all()
        # f_all = FourSrc.objects.all()
        # for i in t_all:
        #     for j in f_all:
        #         if i.username == j.username:
        #             i.four_src_id = j.id
        #             i.save()
        return resp(data='success')
