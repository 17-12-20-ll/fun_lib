import time

from django.db import models

# Create your models here.
from user.models import Group, User


class TradeType(models.Model):
    name = models.CharField(max_length=64, verbose_name='充值类型名称')
    url = models.CharField(max_length=128, verbose_name='淘宝链接')
    price = models.IntegerField(verbose_name='价格')
    group = models.ForeignKey(Group, related_name='t', on_delete=models.CASCADE, null=True, verbose_name='权限组')
    days = models.IntegerField(verbose_name='天数')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'days': self.days,
            'group': self.group_id,
            'url': self.url
        }

    def to_front_dict(self):
        return {
            'id': self.id,
            'vip': self.name,
            'price': self.price,
            'url': self.url
        }

    def to_name_dict(self):
        return {
            'id': self.id,
            'name': self.name
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


class CardRechargeList(models.Model):
    """卡密充值列表"""
    card_id = models.CharField(max_length=32, verbose_name='卡号')
    card_pwd = models.CharField(max_length=32, verbose_name='密码')
    trade_type = models.ForeignKey(TradeType, related_name='r_t', on_delete=models.CASCADE, null=True,
                                   verbose_name='充值类型')
    # 卡号是否使用 （0代表未使用  1代表已经使用  默认是0）
    is_use = models.IntegerField(default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'card_pwd': self.card_pwd,
            'trade_type_id': self.trade_type_id
        }

    def export_list(self):
        return [self.card_id, self.card_pwd, self.trade_type.name]

    class Meta:
        db_table = 'card_recharge_list'


class Order(models.Model):
    id = models.CharField(max_length=128, verbose_name='订单id', primary_key=True)
    login_name = models.CharField(max_length=32, verbose_name='登陆名')
    trade_type = models.IntegerField(verbose_name='充值类型')  # 1: 支付宝 2: 微信 3: 卡密
    # 如果充值类型为卡密自助充值 则存在卡号
    card_id = models.CharField(max_length=128, verbose_name='充值卡号')
    trade_group = models.IntegerField(verbose_name='支付分类')
    total = models.FloatField(verbose_name='充值金额')
    days = models.IntegerField(verbose_name='有效期')
    add_time = models.DateTimeField(verbose_name='充值时间', auto_now_add=True)
    desc = models.CharField(max_length=32, verbose_name='备注')

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.login_name,
            'trade_type': self.trade_type,
            'card_id': self.card_id,
            'total': self.total,
            'days': self.days,
            'add_time': self.add_time,
            'desc': self.desc,
        }

    class Meta:
        db_table = 'order'
