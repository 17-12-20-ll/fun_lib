from django.db import models

# Create your models here.
from user.models import Group, User


class TradeType(models.Model):
    name = models.CharField(max_length=64, verbose_name='充值类型名称')
    price = models.IntegerField(verbose_name='价格')
    group = models.ForeignKey(Group, related_name='t', on_delete=models.SET_NULL, null=True, verbose_name='权限组')
    days = models.IntegerField(verbose_name='天数')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'days': self.days,
            'group': self.group_id
        }

    class Meta:
        db_table = 'trade_type'


class Invoice(models.Model):
    company = models.CharField(max_length=32, verbose_name='公司名称')
    code = models.CharField(max_length=32, verbose_name='纳税人识别码')
    addr_tel = models.CharField(max_length=128, verbose_name='地址及电话')
    acount = models.CharField(max_length=32, verbose_name='开户行及账号')
    receive_email = models.CharField(max_length=32, verbose_name='接受发票的邮箱')
    receive_user = models.CharField(max_length=16, verbose_name='接受发票的人的名字')
    receive_addr = models.CharField(max_length=32, verbose_name='接受发票的人的地址')
    receive_phone = models.CharField(max_length=16, verbose_name='接受发票的人的电话')
    u = models.ForeignKey(User, related_name='invoices', on_delete=models.CASCADE, verbose_name='用户发票信息，级联删除')

    def to_dict(self):
        return {
            'company': self.company,
            'code': self.code,
            'addr_tel': self.addr_tel,
            'acount': self.acount,
            'receive_email': self.receive_email,
            'receive_user': self.receive_user,
            'receive_addr': self.receive_addr,
            'receive_phone': self.receive_phone,
        }

    class Meta:
        db_table = 'trade_invoice'
