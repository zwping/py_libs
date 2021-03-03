"""
当前工具类满足 基于Navicat Premium维护mysql表结构 + SQLAlchemy执行sql语句
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import ResultProxy


class SQLAlchemy2(SQLAlchemy):
    """SQLAlchemy扩充类, 给予更友好的execute方法
    """

    def execute2(self, sql):
        """ 基于engine的sql执行机制, 本身自带commit/rollback
        :param sql:
        :return: [SQLResult]
        """
        result = None
        err = None
        try:
            result = self.engine.execute(sql)
        except Exception as e:
            err = str(e)
        return SQLResult(bool(result), result, err)


class SQLResult:
    """ 引导其成为java语言风格, 重要的是有.代码提示了
    """
    def __init__(self, state=False, result=ResultProxy, err=''):
        self.state = state
        self.result = result
        self.err = err

    def __str__(self):
        return '【SQLResult】 执行结果:%s 结果:%s 错误:%s' % (self.state, self.result, self.err)

