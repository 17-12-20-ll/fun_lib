import redis as redis

from Happy_library.settings import REDIS_IP


class RedisConn:
    def __init__(self, host, port, pwd, db):
        self.host = host
        self.port = port
        self.pwd = pwd
        self.db = db

    def conn(self):
        """获取redis连接实例"""
        # 该参数用作decode_responses=True python读取出来的不是二进制
        pool = redis.ConnectionPool(host=self.host, port=self.port, password=self.pwd, db=self.db, max_connections=1024,
                                    decode_responses=True)
        conn = redis.Redis(connection_pool=pool)
        return conn

    def save_uset_name(self, name, fingerprint):
        # 先获取redis中是否存在该键x.smembers("clip")
        name = f'{name}_sign'
        cli = self.conn()
        cli.sadd(name, fingerprint)
        # 每一次添加数据，都重置过期时间
        self.set_expire(name, 24 * 60 * 60)

    def get_members_len(self, name):
        """获取当前集合的长度"""
        return self.conn().scard(name)

    def set_expire(self, name, time):
        """设置集合过期时间"""
        name = f'{name}_sign'
        self.conn().expire(name, time)  # 过期时间为5min


# 用于进行用户多线程访问的redis
RD = RedisConn(host=REDIS_IP, port=6379, pwd="funredis", db=1)
if __name__ == '__main__':
    RD.save_uset_name('11', 'adjadadkljaol')
