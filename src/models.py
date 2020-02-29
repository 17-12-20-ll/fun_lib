from django.db import models

# Create your models here.
from user.models import Group
from utils.tools import del_pos


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
        }

    def to_all_dict(self):
        # 返回多个数据
        return {
            'name': self.name,
            'pos': self.pos,
            'twos': del_pos([i.to_front_list_dict() for i in self.twos.all()]),
        }

    class Meta:
        db_table = 'one_src'


class OneSrcGroup(models.Model):
    """用户组和一级资源关联关系"""
    one_src = models.ForeignKey(OneSrc, related_name='og', on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, related_name='go', on_delete=models.DO_NOTHING)

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
        }

    def to_list_dict(self):
        return {
            'name': self.name,
            'pos': self.pos,
            'one_src': self.one_src.name,
            'threes': del_pos([i.to_simple_dict() for i in self.threes.all()]),
            'add_time': self.add_time,
        }

    def to_front_list_dict(self):
        # 根据三级资源的有无，返回二级资源是否有下拉和url
        tmp = self.threes.all()
        if len(tmp) > 0:
            return {
                'name': self.name,
                'pos': self.pos,
                'one_src': self.one_src.name,
                'threes': del_pos([i.to_simple_dict() for i in tmp]),
            }
        else:
            return {
                'name': self.name,
                'pos': self.pos,
                'url': self.title_url,
                'one_src': self.one_src.name,
            }

    class Meta:
        db_table = 'two_src'


class ThreeSrc(models.Model):
    """三级资源"""
    name = models.CharField(max_length=32, verbose_name='三级资源名称')
    desc = models.CharField(max_length=1024, verbose_name='描述')
    pos = models.IntegerField(verbose_name='排序字段')
    url = models.CharField(max_length=255, verbose_name='url链接')
    username = models.CharField(max_length=64, verbose_name='登录用户名')
    pwd = models.CharField(max_length=64, verbose_name='登录用户密码')
    username_field = models.CharField(max_length=255, verbose_name='用户名字段')
    pwd_field = models.CharField(max_length=255, verbose_name='密码字段')
    two_src = models.ForeignKey(TwoSrc, related_name='threes', on_delete=models.SET_NULL, null=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    four_src = models.ForeignKey('FourSrc', related_name='fours', on_delete=models.SET_NULL, null=True)

    def to_simple_dict(self):
        return {
            'id': self.id,
            'name': self.name + (self.four_src.name if self.four_src else 'nono'),
            # 'url': self.url,
            'pos': self.pos
        }

    class Meta:
        db_table = 'three_src'


class FourSrc(models.Model):
    name = models.CharField(max_length=32, verbose_name='大学名')
    code = models.CharField(max_length=32, verbose_name='大学编码')
    desc = models.CharField(max_length=128, verbose_name='描述')
    username = models.CharField(max_length=32, verbose_name='账号')
    pwd = models.CharField(max_length=32, verbose_name='密码')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    def to_detail_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'desc': self.desc,
            'username': self.username,
            'pwd': self.pwd,
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

    class Meta:
        db_table = 'four_src'
