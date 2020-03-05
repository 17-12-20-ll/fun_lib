from django.db import models

from user.models import Group


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


class CardRechargeList(models.Model):
    """卡密充值列表"""
    card_id = models.CharField(max_length=32, verbose_name='卡号')
    card_pwd = models.CharField(max_length=32, verbose_name='密码')
    card_count = models.CharField(max_length=32, verbose_name='卡密数量')
    card_num = models.CharField(max_length=32, verbose_name='卡密位数')
    trade_type = models.ForeignKey(TradeType, related_name='r_t', on_delete=models.SET_NULL, null=True, verbose_name='充值类型')
    # group = models.ForeignKey(Group, related_name='c', on_delete=models.SET_NULL, null=True, verbose_name='会员组')
    # 卡号是否使用 （0代表未使用  1代表已经使用  默认是0）
    is_use = models.IntegerField(default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'card_pwd': self.card_pwd,
            'trade_type_id': self.trade_type_id
        }

    class Meta:
        db_table = 'card_recharge_list'
