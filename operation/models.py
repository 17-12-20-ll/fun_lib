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


class HelpClass(models.Model):
    """帮助分类列表"""
    name = models.CharField(max_length=255, verbose_name='帮助分类名称')
    desc = models.CharField(max_length=1024, verbose_name='帮助分类描述')
    pos = models.IntegerField(verbose_name='序号')

    def to_detail_dict(self):
        """返回单个详情数据"""
        return {
            'name': self.name,
            'desc': self.desc,
            'pos': self.pos
        }

    def to_list_dict(self):
        """返回多个数据"""
        return {
            'name': self.name,
            'pos': self.pos
        }

    class Meta:
        db_table = 'help_class'


class HelpList(models.Model):
    """帮助列表"""
    name = models.CharField(max_length=255, verbose_name='帮助列表名称')
    desc = models.CharField(max_length=1024, verbose_name='帮助列表描述')
    pos = models.IntegerField(verbose_name='序号')
    help_class = models.ForeignKey(HelpClass, related_name='help', on_delete=models.SET_NULL, null=True)

    def to_detail_dict(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'pos': self.pos,
            'help_class': self.help_class.name
        }

    def to_list_dict(self):
        # 返回多个数据
        return {
            'name': self.name,
            'pos': self.pos
        }

    class Meta:
        db_table = 'help_list'













