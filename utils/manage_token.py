import hashlib
import time
from django.core import signing

# 对称加密 ， 盐值
KEY = 'fun_lib'
SALT = '1096195574@qq.com'
HEADER = {'typ': 'JWP', 'alg': 'default'}


def get_data_obj(**kwargs):
    """
    iat:
    代表保存token时的时间戳
    expire:
    token存活时间
    active:
    当前是否退出 0 退出 1 激活
    """
    kwargs['iat'] = time.time()
    return kwargs


# print(get_data_obj(id=1, expire=24 * 60 * 60))


def encrypt(obj):
    """加密"""
    # salt给生成的签名加盐，进行解码的时候使用
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw


def create_token(obj):
    """生成token信息保存到缓存中，并返回token"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = obj
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    return "%s.%s.%s" % (header, payload, signature)


def get_payload(token):
    """获取负载信息，存储的信息"""
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload


def check_token(token):
    try:
        obj = get_payload(token)
    except IndexError:
        return None
    # 获取当前时间戳
    cur_time = time.time()
    if obj['expire'] + obj['iat'] >= cur_time:
        return obj
    else:
        return None


if __name__ == '__main__':
    print(create_token(get_data_obj(id=1, expire=60)))
    token = 'ZXlKMGVYQWlPaUpLVjFBaUxDSmhiR2NpT2lKa1pXWmhkV3gwSW4wOjFqMm5NVjpvTnY1THZuUW1hNk95dk5kUzNCUzNjU1hHbTQ.ZXlKcFpDSTZNU3dpWlhod2FYSmxJam8yTUN3aWFXRjBJam94TlRneE56TTBNelU1TGprek5UTTVNVEo5OjFqMm5NVjp2Q0VUV0JjM29FRjBRUTAtYU1nejRvNDloQ1U.b98bd427fba366d549d13d35cd58a145'
    print(check_token(token))
