from django.db import models

# Create your models here.
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
