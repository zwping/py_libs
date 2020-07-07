import datetime
import functools
import time
import traceback

from sqlalchemy import create_engine

from config import db, app
from libs.decorator import func_overtime, sqlalchemy_ctx
from libs.empty_util import isEmpty, isNotEmpty
from libs.log import i
from libs.py_explain import PyExplain


class Explain(PyExplain):

    def file_explain(self):
        return '操作数据库工具集'

    def why_func(self):
        DB.create1()
        DB.create()
        DB.delete()
        DB.update()
        DB.retrieve()
        DBSup.execute('')
        DBSup.retrieveWholes('')
        DBSup.form_where('')
        DBSup.retrieveFixCN('', ())
        DBImpl.execute('', '')
        DBImpl.commit()
        ConstantSql.column_name('', '')


class DB:

    ############ SQL原子操作 #############

    @staticmethod
    def create1(table: str, data: dict, last_row_id=False, bind=None):
        ks = []
        vs = []
        for k in data:
            v = data[k]
            if isNotEmpty(v):
                ks.append(k)
                vs.append(v)
        return DB.create(table, tuple(ks), tuple(vs), last_row_id, bind)

    @staticmethod
    @func_overtime(0.5)
    @sqlalchemy_ctx()
    def create(table: str, keys: tuple, values: tuple, last_row_id=False, bind=None):
        # insert into table (k1,k2) values ('v1',v2)
        keys = str(keys).replace(",", "") if len(keys) == 1 else keys
        values = str(values).replace(",", "") if len(values) == 1 else values
        r = DBImpl.execute("INSERT INTO %s %s VALUES %s" %
                           (table,
                            str(keys).replace("'", '').replace("\"", ''),
                            values),
                           bind)
        last_id = True
        if last_row_id:
            last_id = r.lastrowid  # 获取最近插入的主键id
        if bool(r) and DBImpl.commit():
            return last_id if last_row_id else True
        return False

    @staticmethod
    @func_overtime(0.5)
    @sqlalchemy_ctx()
    def retrieve(sql, fetchone=False, bind=None):
        """ sql查询
        :return
            if fetchone:
                None or
            else:
                [] or [data]
        """
        d = DBImpl.execute(sql, bind)
        if fetchone:
            return d if d is None else d.fetchone()  # tuple
        else:
            return d if d is None else d.fetchall()  # list(tuple)

    @staticmethod
    @func_overtime(0.5)
    @sqlalchemy_ctx()
    def update(table: str, values: dict, where: str = None, bind=None):
        # update table set k1='v1',k2='v2' where k3=v3
        if bool(DBImpl.execute('UPDATE %s SET %s%s' % (table,
                                                       ','.join(
                                                           "%s=%s" % (
                                                                   k, DB.special_value(str(v)))
                                                           for k, v in values.items() if isNotEmpty(v)),
                                                       '' if where is None else ' WHERE %s' % where), bind)):
            return DBImpl.commit()
        return False

    @staticmethod
    def special_value(v):
        """ 特殊值的处理 db在操作update时，value可用sql语法糖来操作，这时不需要对外部value加'' """
        return v if 'concat(' in v and len(v) > 6 and v[:7] == 'concat(' else "'%s'" % v

    @staticmethod
    @func_overtime(0.5)
    @sqlalchemy_ctx()
    def delete(table: str, where: str = None, bind=None):
        # delete from table where k1=v1,k2=v2
        if bool(DBImpl.execute('DELETE FROM %s%s' % (table, '' if where is None else ' WHERE %s' % where), bind)):
            return DBImpl.commit()
        return False

    ############ SQL原子操作 #############

    # //////////////////////////////////
    @staticmethod
    def conv_dic_list_of_column(columns, ls):
        """ 按照列来 """
        r = []
        from collections import OrderedDict
        for it in ls:
            dic = OrderedDict()
            for i, it1 in enumerate(it):
                dic[columns.split(',')[i]] = it1
            r.append(dic)
        return r


class DBSup:

    @staticmethod
    def execute(sql: str, commit=False, result=False, json_key: tuple = (), last_row_id=False, bind=None):
        """ 纯原生执行sql，可在内天马行空的写sql
        :param sql sql语句
        :param commit 是否提交事务
        :param result 是否返回结果 []
        :param last_row_id 是否返回最近插入的id
        :param json_key 返回带有key的json集合[]
        """
        r = DBImpl.execute(sql, bind)
        is_json = isNotEmpty(json_key)
        if result or is_json:
            r1 = None if r is None else \
                [DBSup.__tuple_cov_json(json_key, d) for d in r.fetchall()] if is_json else \
                    r.fetchall()
        elif last_row_id:
            r1 = r.lastrowid
        else:
            r1 = r
        if r:
            if commit:
                if DBImpl.commit():
                    return r1
                else:
                    return False
            else:
                return r1
        return False

    @staticmethod
    def retrieveWholes(sql: str, column_names: tuple = None, fetchone=False, bind=None):
        """ 查询整张表字段数据，返回JSON
        :param sql
        :param column_names 需要返回的json key ,需和sql中查询字段对于
        :param fetchone 只取一个
         """
        if isEmpty(column_names):
            import re
            re1 = re.search('from.\w*', sql)
            if isEmpty(re1):
                raise Exception('正则错误，获取表名失败，不支持的sql语句 %s' % sql)
            table_name = re1.group().replace('from ', '')
            t = DB.retrieve(
                ConstantSql.column_name(
                    table_name,
                    app.config['DATABASE_NAME'])  # todo appConfig中需要增加DATABASE_NAME
                , bind)  # 获取表字段
            if isEmpty(t):
                i('查询表列名出错 %s' % traceback.format_exc())
                raise Exception('查询表列名出错')
            column_names = tuple(s[0] for s in t)
        elif '*' in sql:
            sql = sql.replace('*', str(column_names).replace('(', '').replace(')', '').replace("'", ''))

        r = DB.retrieve(sql, fetchone, bind)
        if isEmpty(r):
            return None if fetchone else []
        if fetchone:
            return DBSup.__tuple_cov_json(column_names, r)
        else:
            return [DBSup.__tuple_cov_json(column_names, d) for d in r]

    @staticmethod
    def retrieveFixCN(sql: str, column_names: tuple, fetchone=False, bind=None):
        """ 查询返回固定的字段名数据
        :param sql 必须查询*
        :param column_names
        :param fetchone 只取一个
        """
        r = DB.retrieve(sql.replace('*',
                                    str(column_names)
                                    .replace('(', '').replace(')', '').replace("'", '')),
                        fetchone, bind)
        if isEmpty(r):
            return None if fetchone else []
        if fetchone:
            return DBSup.__tuple_cov_json(column_names, r)
        else:
            return [DBSup.__tuple_cov_json(column_names, d) for d in r]

    @staticmethod
    def __tuple_cov_json(column_names, t: tuple):
        """ 将元组转换为json
        """
        data = {}
        for i, d in enumerate(tuple(t)):
            data.update({column_names[i]: d
            if not (isinstance(d, datetime.datetime) | isinstance(d, datetime.date))
            else int(time.mktime(d.timetuple()))})
        return data

    @staticmethod
    def form_where(form, *keys, add_where=True):
        """ form中直接提取where条件
        :param form Form
        :param keys {'key','='}(key),{'key','like'},{'key','<='}...
        :param add_where 是否增加where关键字
        :returns: '' / 'where k=v and k=v' / 'k=v and k=v'
        """
        s = []
        for ks in keys:
            if isinstance(ks, dict):
                k = list(ks.keys())[0]
                j = ks[k]
            elif isinstance(ks, str):
                k = ks
                j = '='
            else:
                raise Exception('未知类型')
            v = form.__dict__[k].data
            if isNotEmpty(v):
                s.append("%s %s '%s'" % ('ctime' if k == 'stime' or k == 'etime' else k,
                                         j,
                                         '%{}%'.format(v) if j == 'like' else v))
        r = ' and '.join(s) if isNotEmpty(s) else ''
        return '' if isEmpty(r) else 'where %s' % r if add_where else r


__binds = {}
""" 全局对象，用于实现session一对多数据库连接
"""


def _binds(bind):
    """ 获取bind对象
    :param bind config-binds对象的key
    """
    global __binds
    if not __binds:
        for k, v in app.config['SQLALCHEMY_BINDS'].items():
            __binds.update({k: create_engine(v)})
    return __binds.get(bind)


class DBImpl:

    @staticmethod
    def execute(sql, bind):
        """ 执行sql语句
        """
        i(sql)
        return db.session.execute(sql, bind=_binds(bind))  # 目前只有子线程执行sql才会报错，sqlalchemy_ctx会处理子线程异常
        # try:
        #     return db.session.execute(sql, bind=_binds(bind))
        # except Exception as e:
        #     i('db execute 报错%s' % e)
        #     try:
        #         with app.app_context():
        #             return db.session.execute(sql, bind=_binds(bind))
        #     except Exception as e:
        #         print(traceback.format_exc())
        #         return None

    @staticmethod
    def commit():
        try:
            db.session.commit()
            return True
        except Exception as e:
            i('db commit 报错 %s' % e)
            # i(traceback.format_exc())
            db.session.rollback()
            raise Exception(e)  # 异常上报，让sqlalchemy_ctx补捉处理
            # return False


class ConstantSql:

    @staticmethod
    def column_name(table_name, db_name):
        """ 查询表的列名 """
        return "select column_name from information_schema.COLUMNS where table_schema = '%s' and table_name = '%s'" \
               % (db_name, table_name)
