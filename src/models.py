import json

from django.db import models

# Create your models here.
from user.models import Group
from utils.tools import del_pos
from json_field import JSONField


class OneSrc(models.Model):
    name = models.CharField(max_length=32, verbose_name='一级分类名称')
    desc = models.CharField(max_length=255, verbose_name='分类描述')
    pos = models.IntegerField(verbose_name='资源排序,顺序上升')

    def to_detail_dict(self):
        # 返回单个详情数据
        return {
            'name': self.name,
            'desc': self.desc,
            'pos': self.pos,
            'groups': [i.group.to_name_dict() for i in self.og.all()]
        }

    def to_list_dict(self):
        # 返回多个数据
        return {
            'name': self.name,
            'pos': self.pos,
            'id': self.id
        }

    def to_all_dict(self):
        # 返回多个数据
        return {
            'name': self.name,
            'pos': self.pos,
            'twos': del_pos([i.to_front_list_dict() for i in self.twos.all()]),
        }

    def to_two_dict(self):
        return [i.to_front_list_dict() for i in self.twos.all()]

    class Meta:
        db_table = 'one_src'


class OneSrcGroup(models.Model):
    """用户组和一级资源关联关系"""
    one_src = models.ForeignKey(OneSrc, related_name='og', on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, related_name='go', on_delete=models.DO_NOTHING)

    def to_one_dict(self):
        return [i.to_related_dict() for i in self.one_src.twos.all()]

    def to_two_group_dict(self):
        return [i.to_name_id_dict() for i in self.one_src.twos.all()]

    class Meta:
        db_table = 'one_src_group'


class TwoSrc(models.Model):
    """二级资源"""
    name = models.CharField(max_length=32, verbose_name='二级资源名称')
    title_url = models.CharField(max_length=255, verbose_name="未知字段，但保留了少量数据")
    content = models.CharField(max_length=1024, verbose_name="跳转介绍")
    pos = models.IntegerField(verbose_name='排序字段')
    one_src = models.ForeignKey(OneSrc, related_name='twos', on_delete=models.SET_NULL, null=True)
    src_type = models.IntegerField(verbose_name='资源种类')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def to_detail_dict(self):
        return {
            'name': self.name,
            'title_url': self.title_url,
            'content': self.content,
            'pos': self.pos,
            'src_type': self.src_type,
            'one_src': self.one_src.name,
            'one_src_id': self.one_src.id,
        }

    def to_list_dict(self):
        return {
            'name': self.name,
            'pos': self.pos,
            'one_src': self.one_src.name if self.one_src.name else '',
            'threes': del_pos([i.to_simple_dict() for i in self.threes.all()]),
            'add_time': self.add_time,
        }

    def to_name_id_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'one_src': self.one_src.name if self.one_src else '',
            'add_time': self.add_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def to_front_list_dict(self):
        # 根据三级资源的有无，返回二级资源是否有下拉和url
        tmp = self.threes.all()
        if len(tmp) > 0:
            return {
                'name': self.name,
                'pos': self.pos,
                'one_src': self.one_src.name,
                'threes': del_pos([i.to_front_dict() for i in tmp]),
            }
        else:
            return {
                'name': self.name,
                'pos': self.pos,
                'url': self.title_url,
                'one_src': self.one_src.name,
            }

    def to_update_return(self):
        return {
            'id': self.id,
            'one_name': self.one_src.name,
            'pos': self.pos,
            'two_name': self.name,
            'add_time': self.add_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def to_related_dict(self):
        return [i.id for i in self.threes.all()]

    class Meta:
        db_table = 'two_src'


class ThreeSrc(models.Model):
    """三级资源"""
    name = models.CharField(max_length=32, verbose_name='三级资源名称')
    desc = models.CharField(max_length=1024, verbose_name='描述')
    pos = models.IntegerField(verbose_name='排序字段')
    url = models.CharField(max_length=255, verbose_name='url链接')
    two_src = models.ForeignKey(TwoSrc, related_name='threes', on_delete=models.SET_NULL, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    four_src = models.ForeignKey('FourSrc', related_name='fours', on_delete=models.SET_NULL, null=True)

    def to_simple_dict(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'url': self.url,
            'two_src': self.two_src.name,
            'four_src': self.four_src.name,
            'username': self.four_src.username,
            'pwd': self.four_src.pwd,
            'pos': self.pos,
            'add_time': self.add_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def to_simple_back_dict(self):
        return {
            'name': self.name,
            'desc': self.desc,
            'url': self.url,
            'two_src': self.two_src.id,
            'four_src': self.four_src.id,
            'username': self.four_src.username,
            'pwd': self.four_src.pwd,
            'pos': self.pos,
            'add_time': self.add_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def to_front_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pos': self.pos,
        }

    class Meta:
        db_table = 'three_src'


class FourSrc(models.Model):
    name = models.CharField(max_length=32, verbose_name='大学名')
    code = models.CharField(max_length=32, verbose_name='大学编码')
    url = models.CharField(max_length=255, verbose_name='url链接')
    desc = models.CharField(max_length=128, verbose_name='描述')
    username = models.CharField(max_length=128, verbose_name='账号')
    pwd = models.CharField(max_length=128, verbose_name='密码')
    code_script = models.CharField(max_length=2048, verbose_name='脚本代码存储')
    cookie_time = models.IntegerField(verbose_name='cookie存储时长')
    cookie = JSONField(max_length=2048, verbose_name='存储cookie脚本')
    success_url = models.CharField(max_length=255, verbose_name='url链接')
    error_field = models.CharField(max_length=64, verbose_name='失败检测字段')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def to_detail_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'url': self.url,
            'desc': self.desc,
            'username': self.username,
            'pwd': self.pwd,
            'code_script': self.code_script,
            'cookie_time': self.cookie_time,
            'cookie': json.dumps(self.cookie),
            'success_url': self.success_url,
            'error_field': self.error_field,
            'add_time': self.add_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def to_list_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'username': self.username,
            'pwd': self.pwd,
            'add_time': self.add_time,
        }

    def to_name_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    class Meta:
        db_table = 'four_src'
