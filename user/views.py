import base64
import datetime
import json
import re
import time

from django.db import connection
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from operation.models import AdminLoginLog
from src.models import OneSrc
from user.models import User, Group
from utils.gen_captcha import create_img
from utils.manage_resp import resp
from utils.manage_token import get_data_obj, create_token, check_token
from utils.redis_helper import RD
from utils.send_email import send_mail
from utils.tools import img_code_overdue_decode, img_code_overdue_create


# =======================User=======================
@csrf_exempt
def register(request):
    """注册用户"""
    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        old_u = User.objects.filter(login_name=login_name).first()
        if old_u:
            return resp(1001, '用户名已存在')
        email = request.POST.get('email')
        old_u = User.objects.filter(email=email).first()
        if old_u:
            return resp(1001, '邮箱已注册')
        pwd = request.POST.get('pwd')
        if len(pwd) < 6 or len(pwd) > 16:
            return resp(1002, '密码长度在6-16')
        major = request.POST.get('major')
        user_name = request.POST.get('user_name')
        qq = request.POST.get('qq')
        phone = request.POST.get('phone')
        u = User()
        u.login_name = login_name
        u.pwd = pwd
        u.email = email
        u.major = major
        u.user_name = user_name
        u.qq = qq
        u.phone = phone
        u.save()
        return resp()


@csrf_exempt
def login(request):
    """登录用户"""
    if request.method == 'POST':
        # stus = Student.objects.filter(Q(s_age__lte=18) | Q(s_age__gt=20))  # 或操作
        login_name = request.POST.get('login_name')
        # 获取浏览器指纹，用于校验用户的唯一性，以及多线程登陆该账号
        fp = request.META.get('HTTP_AUTHENTICATION_FP')
        img_token = request.POST.get('img_token')
        try:
            code = int(request.POST.get('code'))
        except:
            return resp(1003, '验证码不规范')
        pwd = request.POST.get('pwd')
        if not img_token:
            return resp(1004, '没有传入验证码序列号')
        token_flag = img_code_overdue_decode(img_token)
        if not token_flag:
            return resp(1001, '验证码过期')
        if code != token_flag['val']:
            return resp(code=1002, msg='验证码错误')
        # 后台登陆标识
        back = request.POST.get('back')
        u = User.objects.filter(
            Q(login_name=login_name) | Q(email=login_name)).first() if not back else User.objects.filter(
            login_name=login_name).filter(is_admin=1).first()
        if not u:
            return resp(201, '当前用户未注册')
        if not back:
            if u.is_admin:
                return resp(203, '管理员不能登陆前端')
        if u.pwd != pwd:
            return resp(202, '密码错误！')
        # 管理员==========
        # 都通过的情况下 表示该用户已经通过校验
        # 如果登陆的是管理员的话，需要记录管理员登陆日志
        if back:
            a_l = AdminLoginLog()
            a_l.login_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            a_l.admin_name = u.login_name
            a_l.save()
        # 用户==========
        # 管理员不需要进行账号线程限制 enable=-1
        # 用户进行线程限制
        # 1. 读取当前id是否
        # RD.save_uset_name(u.id, fp)  # 存储当前用户线程控制指纹
        # 改变用户行为
        ori_op = request.META.get('HTTP_X_FORWARDED_FOR')
        if u.cur_login_ip:
            # 将上次登陆的当前ip赋值给上次ip
            u.last_login_ip = u.cur_login_ip
            u.last_login_time = u.cur_login_time
        u.cur_login_ip = ori_op if ori_op else request.META.get('REMOTE_ADDR')
        u.cur_login_time = datetime.datetime.now()
        if u.login_count:
            u.login_count += 1
        else:
            u.login_count = 1
        u.save()
        # 开始保存用户token
        obj = get_data_obj(id=u.id, expire=24 * 60 * 60)
        token = create_token(obj)
        return resp(data={'token': token, 'login_name': u.login_name})


@csrf_exempt
def forget_email_pwd(request):
    """根据注册的邮箱找回密码"""
    if request.method == 'POST':
        email = request.POST.get('email')
        u = User.objects.filter(email=email).first()
        if not u:
            return resp(201, '用户不存在')
        # 获取唯一验证的字符串，过期时间、用户id，创建时间
        sequence = img_code_overdue_create(id=u.id, _time=time.time(), ex=30 * 60)
        if not u.email:
            return resp(401, '用户未填写邮箱')
        flag = send_mail(u.email, sequence)
        if not flag:
            return resp(402, '发送失败')
        return resp()


@csrf_exempt
def update_forget_email_pwd(request):
    if request.method == 'POST':
        # 获取唯一的标识字符串
        sequence = request.POST.get('sequence')
        pwd = request.POST.get('pwd')
        # 解析字符串
        try:
            obj = img_code_overdue_decode(sequence)
        except:
            obj = ''
        if not obj:
            return resp(401, '失效')
        u_id = obj['id']
        u = User.objects.filter(id=u_id).first()
        u.pwd = pwd
        u.save()
        return resp()


def captcha(request):
    # 生成图形验证码
    if request.method == 'GET':
        _time = time.time()
        img, token = create_img(_time)
        return resp(data={'img': str(base64.b64encode(img), encoding='utf-8'), 'token': token})


def check_img_code(request):
    if request.method == 'GET':
        token = request.GET.get('token')
        val = int(request.GET.get('val'))
        # 一：判断是否是某个时刻发送的
        # 二：判断验证码是否输入正确
        obj = img_code_overdue_decode(token)
        if not obj:
            # token通过校验
            return resp(code=1001, msg='token过期')
        if val != obj['val']:
            return resp(code=1002, msg='验证码错误')
        return resp()


def get_token_info(request):
    """根据token获取用户信息"""
    if request.method == 'GET':
        token = request.META.get('HTTP_AUTHENTICATION')
        back = request.GET.get('back')
        #  解析token数据
        obj = check_token(token)
        if obj:
            u_id = obj['id']
            u = User.objects.filter(id=u_id).first()
            return resp(data=u.to_back_dict() if back else u.to_front_dict())
        else:
            return resp(code=4001, msg='token 失效')


def check_token_result(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        return resp(200) if obj else resp(400)


@csrf_exempt
def update(request):
    """后台修改信息"""
    if request.method == 'POST':
        u_id = request.POST.get("id")
        group_id = request.POST.get('group_id')
        login_name = request.POST.get('login_name')
        pwd = request.POST.get('pwd')
        email = request.POST.get('email')
        major = request.POST.get('major')
        user_name = request.POST.get('user_name')
        qq = request.POST.get('qq')
        phone = request.POST.get('phone')
        end_time = request.POST.get('end_time')
        enable = int(request.POST.get('enable'))
        active = int(json.loads(request.POST.get('active')))
        u = User.objects.filter(id=u_id).first()
        u.group_id = group_id
        u.login_name = login_name
        u.pwd = pwd
        u.email = email
        u.major = major
        u.user_name = user_name
        u.qq = qq
        u.phone = phone
        u.end_time = end_time
        u.enable = enable
        u.active = active
        u.save()
        return resp(data=u.to_back_read_dict())


def format_user_list(data):
    """格式化 用户数据"""
    return {
        'id': data[0],
        'login_name': data[1],
        'user_name': data[2],
        'group_name': data[3],
        # 存在一个充值总金额还未添加字段
        'add_time': data[4].strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': data[5].strftime("%Y-%m-%d %H:%M:%S") if data[5] else '已过期',
        'last_login_ip': data[6],
        'cur_login_ip': data[7],
    }


def get_users(request):
    """后台获取用户数据"""
    if request.method == "GET":
        u_id = request.GET.get('id')
        if u_id:
            """代表查询单条数据"""
            u = User.objects.filter(id=u_id).first()
            if not u:
                return resp(400, '没有该用户')
            return resp(data=u.to_back_read_dict())
        else:
            """代表查询列表数据"""
            cursor = connection.cursor()
            page = int(request.GET.get('p', 1))
            page_num = int(request.GET.get('n', 10))
            sql = f'select a.id,a.login_name,a.user_name,b.name,a.add_time,a.end_time,a.last_login_ip,a.cur_login_ip' \
                  f' from user a join `group` b on a.group_id=b.id ' \
                  f'limit {(page - 1) * page_num},{page_num}'
            cursor.execute(sql)
            cursor.close()
            return resp(data=[format_user_list(i) for i in cursor.fetchall()])


def get_user(request):
    """获取user分页数据，以及检索条件"""
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
                        if i == 'group_id':
                            tmp_l.append(f'a.group_id={d[i]}')
                        elif i == 'login_name':
                            tmp_l.append(f'a.login_name like "%{d[i]}%"')
                        elif i == 'user_name':
                            tmp_l.append(f'a.user_name like "%{d[i]}%"')
                        elif i == 'email':
                            tmp_l.append(f'a.email like "%{d[i]}%"')
            tmp_sql = ' and '.join(tmp_l)
            # 代表有检索条件
            sql = f'select a.id,a.login_name,a.user_name,b.name,a.add_time,a.end_time,a.last_login_ip,a.cur_login_ip' \
                  f' from user a join `group` b on a.group_id=b.id where {tmp_sql}' \
                  f' order by a.id desc limit {(p - 1) * n},{n}'
        else:
            # 代表查询所有数据分页
            sql = f'select a.id,a.login_name,a.user_name,b.name,a.add_time,a.end_time,a.last_login_ip,a.cur_login_ip' \
                  f' from user a join `group` b on a.group_id=b.id ' \
                  f' order by a.id desc limit {(p - 1) * n},{n}'
        cursor.execute(sql)
        data = [format_user_list(i) for i in cursor.fetchall()]
        sql = re.sub(r'a\.id.*?cur_login_ip', 'count(*)', sql)
        sql = sql.split("limit")[0].strip()
        cursor.execute(sql)
        l = cursor.fetchone()
        cursor.close()
        return resp(data=data, count=l[0])


def get_user_count(request):
    """获取所有用户条数"""
    if request.method == 'GET':
        count = User.objects.count()
        return resp(count=count)


@csrf_exempt
def update_profile(request):
    """修改个人信息"""
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        u_id = obj['id']
        email = request.POST.get('email')
        major = request.POST.get('major')
        user_name = request.POST.get('user_name')
        qq = request.POST.get('qq')
        phone = request.POST.get('phone')
        u = User.objects.filter(id=u_id).first()
        if not u:
            return resp(201, 'not user')
        u.email = email
        u.major = major
        u.user_name = user_name
        u.qq = qq
        u.phone = phone
        u.save()
        return resp()


@csrf_exempt
def update_pwd(request):
    """修改密码"""
    if request.method == 'POST':
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        u_id = obj['id']
        u = User.objects.filter(id=u_id).first()
        old_pwd = request.POST.get('old_pwd')
        if not u:
            return resp(201, 'not user')
        if u.pwd != old_pwd:
            return resp(202, 'pwd error')
        new_pwd = request.POST.get('new_pwd')
        u.pwd = new_pwd
        u.save()
        return resp()


def get_user_info(request):
    """根据用户id获取用户信息"""
    if request.method == "GET":
        u_id = request.GET.get('id')
        # 判断当前如何获取的详情数据，分析应当传递后端数据还是前端数据
        # 需要检测token的值，如果传递的是admin则返回后端数据，传递的是普通的数据，返回前端的数据
        token = request.META.get('HTTP_AUTH_TOKEN')
        obj = check_token(token)
        if obj:
            # token通过校验
            check_u = User.objects.filter(id=obj['id']).first()
            if u_id:
                u = User.objects.filter(id=u_id).first()
                return resp(data=u.to_back_dict() if check_u.is_admin else u.to_front_dict())
            else:
                u_all = User.objects.all()
                return resp(data=[i.to_back_dict() for i in u_all])
        else:
            return resp(code=400, msg='处于没有登陆状态')


@csrf_exempt
def add_back_user(request):
    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        old_u = User.objects.filter(login_name=login_name).first()
        if old_u:
            return resp(1001, '用户名已存在')
        email = request.POST.get('email')
        old_u = User.objects.filter(email=email).first()
        if old_u:
            return resp(1001, '邮箱已注册')
        pwd = request.POST.get('pwd')
        if len(pwd) < 6 or len(pwd) > 16:
            return resp(1002, '密码长度在6-16')
        # 获取其他参数
        group_id = request.POST.get('group_id')
        major = request.POST.get('major')
        qq = request.POST.get('qq')
        user_name = request.POST.get('user_name')
        phone = request.POST.get('phone')
        end_time = request.POST.get('end_time')
        enable = int(request.POST.get('enable'))
        active = int(json.loads(request.POST.get('active')))
        u = User()
        u.group_id = group_id
        u.login_name = login_name
        u.email = email
        u.pwd = pwd
        u.major = major
        u.qq = qq
        u.user_name = user_name
        u.phone = phone
        u.end_time = end_time
        u.enable = enable
        u.active = active
        u.save()
        return resp()


def query_user(request):
    if request.method == 'GET':
        d = request.GET
        q = Q()
        for i in d:
            if d[i]:
                tmp = i if i == 'group_id' else i + '__contains'
                q.add(Q(**{tmp: d[i]}), Q.AND)
        data = User.objects.filter(q)
        return resp(data=[i.to_back_read_dict() for i in data])


# =====================管理员====================
@csrf_exempt
def add_admin(request):
    if request.method == 'POST':
        login_name = request.POST.get('login_name')
        user_name = request.POST.get('username')
        pwd = request.POST.get('pwd')
        a = User()
        a.login_name = login_name
        a.user_name = user_name
        a.pwd = pwd
        a.is_admin = 1
        a.save()
        return resp()


def get_admins(request):
    """获取管理员列表"""
    if request.method == 'GET':
        a_id = request.GET.get('id')
        if a_id:
            a = User.objects.filter(id=a_id).filter(is_admin=1).first()
            return resp(data=a.to_admin_view_dict())
        else:
            a_all = User.objects.filter(is_admin=1)
            return resp(data=[i.to_admin_dict() for i in a_all])


@csrf_exempt
def update_admin(request):
    """更新管理员信息"""
    if request.method == 'POST':
        a_id = request.POST.get('id')
        login_name = request.POST.get('login_name')
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        a = User.objects.filter(id=a_id).first()
        a.login_name = login_name
        a.user_name = username
        a.pwd = pwd
        a.save()
        return resp()


def query_admin(request):
    """多条件动态查询数据"""
    if request.method == 'GET':
        d = request.GET
        q = Q()
        for i in d:
            if d[i]:
                tmp = i + '__contains'
                q.add(Q(**{tmp: d[i]}), Q.AND)
        data = User.objects.filter(q).filter(is_admin=1)  # .values('id', 'login_name', 'user_name')
        return resp(data=[i.to_admin_dict() for i in data])


# ====================Group===================
@csrf_exempt
def add_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        g = Group()
        g.name = name
        g.desc = desc
        g.save()
        return resp()


def del_group(request):
    if request.method == 'GET':
        g_id = request.GET.get('id')
        Group.objects.filter(id=g_id).delete()
        return resp()


@csrf_exempt
def update_group(request):
    if request.method == 'POST':
        g_id = request.POST.get('id')
        name = request.POST.get('name')
        desc = request.POST.get('desc')
        g = Group.objects.filter(id=g_id).first()
        g.name = name
        g.desc = desc
        g.save()
        return resp()


def get_group_info(request):
    if request.method == 'GET':
        g_id = request.GET.get('id')
        if g_id:
            """返回单条数据"""
            g = Group.objects.filter(id=g_id).first()
            return resp(data=g.to_full_dict())
        else:
            """返回所有数据"""
            g_all = Group.objects.all()
            return resp(data=[i.to_name_dict() for i in g_all])


def to_group_one_src(request):
    """根据会员分组查找当前分组的所有资源"""
    if request.method == 'GET':
        p = int(request.GET.get('p', 1))
        n = int(request.GET.get('n', 10))
        g_id = request.GET.get('id')
        g = Group.objects.filter(id=g_id).first()
        tmp = [i.to_two_group_dict() for i in g.go.all()]
        data = [j for i in tmp for j in i]
        return resp(data=data[(p - 1) * n:p * n], count=len(data))


def get_to_name_info(request):
    """根据分组名查询分组"""
    if request.method == 'GET':
        name = request.GET.get('name')
        g_all = Group.objects.all()
        if name:
            g_all = Group.objects.filter(name__contains=name)
        return resp(data=[i.to_name_dict() for i in g_all])


def check_user(request):
    if request.method == 'GET':
        token = request.META.get('HTTP_AUTHENTICATION')
        obj = check_token(token)
        if not obj:
            return resp(204, '用户信息过期')
        u_id = obj['id']
        u = User.objects.filter(id=u_id).first()
        end_time = u.end_time
        if not end_time:
            return resp(201, '用户还未购买资源')
        # 获取用户当前时间是否过期
        if datetime.datetime.now() > end_time:
            # 用户过期
            return resp(202, '用户过期')
        # 查询当前用户的资源权限
        group = Group.objects.filter(id=u.group_id).first()
        # 获取当前用户对应的一级分类id
        cursor = connection.cursor()
        sql = f'select a.id from one_src a join one_src_group b on a.id=b.one_src_id join `group` c on ' \
              f'c.id=b.group_id join user d on d.group_id=c.id where d.id={u_id}'
        cursor.execute(sql)
        one_src_id_list = [str(i[0]) for i in cursor.fetchall()]
        sql = f'select a.id from one_src a left join two_src b on a.id=b.one_src_id left join three_src c ' \
              f'on b.id=c.two_src_id where a.id in ({",".join(one_src_id_list)});'
        cursor.execute(sql)
        data = OneSrc.objects.filter(id__in=[i for i in {i[0] for i in cursor.fetchall()}])
        cursor.close()
        data = [i.to_all_dict() for i in data]
        return resp(data=data)
