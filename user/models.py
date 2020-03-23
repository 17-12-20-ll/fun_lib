from django.db import models


# Create your models here.


class User(models.Model):
    # 注意：累积金额从用户充值的金额累加 ,分组待模型
    login_name = models.CharField(max_length=32, unique=True, null=False, verbose_name='登录名')
    pwd = models.CharField(max_length=32, null=False, verbose_name='密码')
    cur_login_ip = models.CharField(max_length=32, verbose_name='本次登录ip')
    cur_login_time = models.DateTimeField(verbose_name='当前登录时间')
    last_login_ip = models.CharField(max_length=32, verbose_name='最后一次登录ip')
    last_login_time = models.DateTimeField(verbose_name='最后一次登录时间')
    user_name = models.CharField(max_length=16, verbose_name='用户名或公司名')
    phone = models.CharField(max_length=11, verbose_name='用户电话')
    major = models.CharField(max_length=32, verbose_name='专业方向')
    qq = models.CharField(max_length=16, verbose_name='qq')
    email = models.CharField(max_length=16, unique=True, verbose_name="邮箱")
    enable = models.IntegerField(verbose_name='用户可用线程数', default=1)
    active = models.IntegerField(verbose_name='用户是否锁定', default=1)
    is_admin = models.IntegerField(verbose_name='是否为admin')
    end_time = models.DateTimeField(verbose_name='有效时间', auto_now_add=True)
    login_count = models.IntegerField(verbose_name='登录统计')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='新建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    group = models.ForeignKey('Group', related_name='users', default=1, null=True, on_delete=models.SET_NULL)
    is_del = models.IntegerField(verbose_name='是否删除', default=0)

    def to_back_dict(self):
        return {
            'id': self.id,
            'group': self.group.name,
            'login_name': self.login_name,
            'pwd': self.pwd,
            'cur_login_ip': self.cur_login_ip,
            'cur_login_time': self.cur_login_time.strftime("%Y-%m-%d %H:%M:%S"),
            'last_login_time': self.last_login_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_login_time else None,
            'last_login_ip': self.last_login_ip,
            'user_name': self.user_name,
            'phone': self.phone,
            'major': self.major,
            'qq': self.qq,
            'email': self.email,
            'enable': self.enable,
            'is_admin': self.is_admin,
            'end_time': self.end_time if self.end_time else None,
            'login_count': self.login_count,
            'add_time': self.add_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def to_front_dict(self):
        return {
            'id': self.id,
            'group': self.group.name,
            'login_name': self.login_name,
            'email': self.email,
            'user_name': self.user_name,
            'phone': self.phone,
            'last_login_time': self.last_login_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_login_time else '',
            'cur_login_time': self.cur_login_time.strftime("%Y-%m-%d %H:%M:%S"),
            'enable': self.enable,
            'end_time': self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else None,
            'major': self.major,
            'qq': self.qq,
            'login_count': self.login_count,
            'last_login_ip': self.last_login_ip,
            'cur_login_ip': self.cur_login_ip,
        }

    def to_admin_dict(self):
        return {
            'id': self.id,
            'login_name': self.login_name,
            'username': self.user_name,
            'role_name': '管理员'
        }

    def to_admin_view_dict(self):
        return {
            'id': self.id,
            'login_name': self.login_name,
            'username': self.user_name,
            'pwd': self.pwd,
            'role_name': '管理员'
        }

    def to_back_read_dict(self):
        return {
            'id': self.id,
            'group_id': self.group.id,
            'group_name': self.group.name,
            'login_name': self.login_name,
            'pwd': self.pwd,
            'email': self.email,
            'major': self.major,
            'user_name': self.user_name,
            'qq': self.qq,
            'phone': self.phone,
            'end_time': self.end_time if self.end_time else None,
            'enable': self.enable,
            'active': self.active
        }

    class Meta:
        db_table = 'user'


class Group(models.Model):
    """用户组"""
    name = models.CharField(max_length=16, verbose_name='用户组名称')
    desc = models.CharField(max_length=255, verbose_name='用户组描述')

    def to_name_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def to_full_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'desc': self.desc
        }

    class Meta:
        db_table = 'group'
