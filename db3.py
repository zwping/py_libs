""" 基于pymysql + dbutils 连接池的封装
pymysql doc:    https://github.com/PyMySQL/PyMySQL
dbutils doc:    https://github.com/WebwareForPython/DBUtils
examples:
    flask App.py
        db = DBHelper().init_db_params(...)
    demo.py
        from App import db
        with db.getconn2() as conn:
            sql = 'select * from `demo_table`'
            if conn.execute(sql) != -1:
                print(conn.fetchall())
                # conn.commit()
"""

import pymysql
from dbutils.pooled_db import PooledDB


class ConnPool(object):
    """ 创建PooledDB格式的数据库连接池
    """
    __pool = None

    def __init__(self, host, port, user, pwd, db, charset):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.charset = charset

    def __getconn(self):
        if self.__pool is None:
            self.__pool = PooledDB(
                creator=pymysql,  # 使用链接数据库的模块
                maxconnections=0,  # 连接池允许的最大连接数，0和None表示不限制连接数
                mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
                maxshared=1,    # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                ping=0,         # ping MySQL服务端，检查是否服务可用。0 = None = never, 1 = default / 2 / 4 / 7
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.pwd,
                database=self.db,
                charset=self.charset
            )
        return self.__pool.connection()

    def getconn(self):
        conn = self.__getconn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)    # 游标内的值为dict
        return cursor, conn


class DBHelper(object):
    """ pymysql升级版, 代码实现思路与pymysql重叠 """

    _db = None

    def init_db_params(self, host, port, user, pwd, db, charset):
        self._db = ConnPool(host, port, user, pwd, db, charset)
        return self

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'inst'):  # 单例
            cls.inst = super(DBHelper, cls).__new__(cls, *args, **kwargs)
        return cls.inst

    def getconn2(self):
        """ 从连接池中取出一个连接, 同时装箱至ConnBoxing """
        return ConnBoxing(self._db.getconn())


class ConnBoxing(object):
    """ course, conn 操作装箱
    examples:
        with db.getconn2() as conn:
            sql = 'select * from `demo_table`'
            if conn.execute(sql, params) != -1:
                # conn.commit()
                print(conn.fetchall())
    """

    def __init__(self, conn):
        self.cursor, self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, param: tuple = None):
        """ sql 执行
        :param sql:
        :param param:
        :return: 改变的数据条数, 也可做为是否成功 -1
        """
        try:
            # print(sql % param if param is not None else sql)
            if param:
                return self.cursor.execute(sql, param)
            else:
                return self.cursor.execute(sql)
        except Exception as e:
            print('\033[1;31m' + str(e) + ' sql: {} % {}'.format(sql, param) + '\033[0m')
            self.conn.rollback()
            return -1

    def commit(self):
        self.conn.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def lastrowid(self):    # insert主键id
        return self.cursor.lastrowid

