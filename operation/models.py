from django.db import models


# Create your models here.

class AdminLoginLog(models.Model):
    """管理员登陆日志"""
    login_time = models.DateTimeField(auto_now_add=True, verbose_name='管理员登陆时间')
    admin_name = models.CharField(max_length=64, verbose_name='管理员登陆名')
    login_ip = models.CharField(max_length=32, verbose_name='登陆ip')

    def to_dict(self):
        return {
            'admin_name': self.admin_name,
            'login_time': self.login_time,
            'login_ip': self.login_ip
        }

    class Meta:
        db_table = 'admin_login_log'


class UserLoginLog(models.Model):
    """会员登陆日志"""
    login_name = models.CharField(max_length=32, verbose_name='用户登陆名')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')
    login_ip = models.CharField(max_length=32, verbose_name='登陆ip')
    operation = models.CharField(max_length=1024, verbose_name='点击资源链接')

    class Meta:
        db_table = 'user_login_log'
