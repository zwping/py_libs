import datetime
import threading
import time
import traceback

from libs.decorator import func_overtime
from libs.empty_util import isEmpty
# from spider.service_log import service_log
from config import db, app


class DB:

    ############ SQL原子操作 #############

    @staticmethod
    @func_overtime(0.5)
    def create(table: str, keys: tuple, values: tuple):
        # insert into table (k1,k2) values (v1,v2)
        keys = str(keys).replace(",", "") if len(keys) == 1 else keys
        values = str(values).replace(",", "") if len(values) == 1 else values
        if bool(DB.__execute("INSERT INTO %s %s VALUES %s" % (table, str(keys).replace("'", ""), values))):
            return DB.__commit()
        return False

    @staticmethod
    @func_overtime(0.5)
    def retrieve(sql, fetchone=False):
        """ sql查询
        :return
            if fetchone:
                None or
            else:
                [] or [data]
        """
        d = DB.__execute(sql)
        if fetchone:
            return d if d is None else d.fetchone()  # tuple
        else:
            return d if d is None else d.fetchall()  # list(tuple)

    @staticmethod
    @func_overtime(0.5)
    def update(table: str, values: dict, where: str = None):
        # update table set k1='v1',k2='v2' where k3=v3
        if bool(DB.__execute('UPDATE %s SET %s%s' % (table,
                                                     ','.join(
                                                         "%s=%s" % (k, DB.special_value(str(v)))
                                                         for k, v in values.items()),
                                                     '' if where is None else ' WHERE %s' % where))):
            return DB.__commit()
        return False

    @staticmethod
    def special_value(v):
        """ 特殊值的处理 db在操作update时，value可用sql语法糖来操作，这时不需要对外部value加'' """
        return v if 'concat(' in v and len(v) > 6 and v[:7] == 'concat(' else "'%s'" % v

    @staticmethod
    @func_overtime(0.5)
    def delete(table: str, where: str = None):
        # delete from table where k1=v1,k2=v2
        if bool(DB.__execute('DELETE FROM %s%s' % (table, '' if where is None else ' WHERE %s' % where))):
            return DB.__commit()
        return False

    ############ SQL原子操作 #############

    @staticmethod
    def __execute(sql):
        """ 执行sql语句
        针对context的兼容性问题，更建议在子线程执行sql前with一下
        """
        # from libs.log import i
        # i(sql)
        # print(sql)
        try:
            return db.session.execute(sql)
        except Exception as e:
            try:
                with app.app_context():
                    return db.session.execute(sql)
            except Exception as e:
                # service_log("SQL执行错误", traceback.format_exc())
                return None

    @staticmethod
    def __commit():
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            print(traceback.format_exc())
            return False

    # except Exception:
    #     try:
    #         with app.app_context():
    #             db.session.commit()
    #             return True
    #     except Exception as e:
    #         service_log("SQL事务提交错误", traceback.format_exc())
    #         return False

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
    def retrieveWholes(sql: str, column_names: tuple = None, fetchone=False):
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
            from config.constant_sql import ConstantSql
            t = DB.retrieve(ConstantSql.SQL.column_name(table_name))  # 获取表字段
            if isEmpty(t):
                raise Exception('查询表列名出错')
            column_names = tuple(s[0] for s in t)

        r = DB.retrieve(sql, fetchone)
        if isEmpty(r):
            return None
        if fetchone:
            return DBSup.__tuple_cov_json(column_names, r)
        else:
            lists = []
            for d in r:
                lists.append(DBSup.__tuple_cov_json(column_names, d))
            return lists

    @staticmethod
    def retrieveFixCN(sql: str, column_names: tuple, fetchone=False):
        """ 查询返回固定的字段名数据
        :param sql 必须查询*
        :param column_names
        :param fetchone 只取一个
        """
        r = DB.retrieve(sql.replace('*',
                                    str(column_names)
                                    .replace('(', '').replace(')', '').replace("'", '')),
                        fetchone)
        if isEmpty(r):
            return None
        if fetchone:
            return DBSup.__tuple_cov_json(column_names, r)
        else:
            lists = []
            for d in r:
                lists.append(DBSup.__tuple_cov_json(column_names, d))
            return lists

    @staticmethod
    def __tuple_cov_json(column_names, t: tuple):
        """ 将元组转换为json
        """
        data = {}
        for i, d in enumerate(tuple(t)):
            data.update({column_names[i]
                         : d
                if not (isinstance(d, datetime.datetime) | isinstance(d, datetime.date))
                else int(time.mktime(d.timetuple()))})
        return data
