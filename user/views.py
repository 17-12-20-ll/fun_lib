import base64
import time

from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from operation.models import AdminLoginLog
from user.models import User, Group
from utils.gen_captcha import create_img
from utils.manage_resp import resp
from utils.manage_token import get_data_obj, create_token, check_token
from utils.tools import timestamp_to_str, img_code_overdue_decode


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
        img_token = request.POST.get('img_token')
        try:
            code = int(request.POST.get('code'))
        except:
            return resp(1003, '验证码不规范')
        pwd = request.POST.get('pwd')
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
        if u.pwd != pwd:
            return resp(202, '密码错误！')
        # 都通过的情况下 表示该用户已经通过校验
        # 如果登陆的是管理员的话，需要记录管理员登陆日志
        if back:
            a_l = AdminLoginLog()
            a_l.login_ip = request.META.get('HTTP_X_FORWARDED_FOR')
            a_l.admin_name = u.login_name
            a_l.save()
        # 改变用户行为
        ori_op = request.META.get('HTTP_X_FORWARDED_FOR')
        if u.cur_login_ip:
            # 将上次登陆的当前ip赋值给上次ip
            u.last_login_ip = u.cur_login_ip
            u.last_login_time = u.cur_login_time
        u.cur_login_ip = ori_op if ori_op else request.META.get('REMOTE_ADDR')
        u.cur_login_time = timestamp_to_str()
        if u.login_count:
            u.login_count += 1
        else:
            u.login_count = 1
        u.save()
        # 开始保存用户token
        obj = get_data_obj(id=u.id, expire=24 * 60 * 60)
        token = create_token(obj)
        return resp(data={'token': token, 'login_name': u.login_name})


def forget_email_pwd(request):
    if request.method == 'POST':
        pass


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


def update(request):
    """后台修改信息"""
    if request.method == 'POST':
        group = request.POST.get('group')
        login_name = request.POST.get('login_name')
        pwd = request.POST.get('pwd')
        email = request.POST.get('email')
        major = request.POST.get('major')
        user_name = request.POST.get('user_name')
        qq = request.POST.get('qq')
        phone = request.POST.get('phone')
        pass


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
        if not token:
            return resp(code=400, msg='处于没有登陆状态')
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
            return resp(data=g.to_name_dict())
        else:
            """返回所有数据"""
            g_all = Group.objects.all()
            return resp(data=[i.to_full_dict() for i in g_all])
