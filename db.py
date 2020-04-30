import datetime
import time
import traceback

from config import db, app
from libs.decorator import func_overtime
from libs.empty_util import isEmpty, isNotEmpty
from libs.log import i


class DB:

    ############ SQL原子操作 #############

    @staticmethod
    @func_overtime(0.5)
    def create1(table: str, data: dict, last_row_id=False):
        ks = []
        vs = []
        for k in data:
            v = data[k]
            if isNotEmpty(v):
                ks.append(k)
                vs.append(v)
        return DB.create(table, tuple(ks), tuple(vs), last_row_id)

    @staticmethod
    @func_overtime(0.5)
    def create(table: str, keys: tuple, values: tuple, last_row_id=False):
        # insert into table (k1,k2) values ('v1',v2)
        keys = str(keys).replace(",", "") if len(keys) == 1 else keys
        values = str(values).replace(",", "") if len(values) == 1 else values
        r = DBImpl.execute("INSERT INTO %s %s VALUES %s" %
                           (table,
                            str(keys).replace("'", '').replace("\"", ''),
                            values))
        last_id = True
        if last_row_id:
            last_id = r.lastrowid  # 获取最近插入的主键id
        if bool(r) and DBImpl.commit():
            return last_id if last_row_id else True
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
        d = DBImpl.execute(sql)
        if fetchone:
            return d if d is None else d.fetchone()  # tuple
        else:
            return d if d is None else d.fetchall()  # list(tuple)

    @staticmethod
    @func_overtime(0.5)
    def update(table: str, values: dict, where: str = None):
        # update table set k1='v1',k2='v2' where k3=v3
        if bool(DBImpl.execute('UPDATE %s SET %s%s' % (table,
                                                       ','.join(
                                                           "%s=%s" % (
                                                                   k, DB.special_value(str(v)))
                                                           for k, v in values.items() if isNotEmpty(v)),
                                                       '' if where is None else ' WHERE %s' % where))):
            return DBImpl.commit()
        return False

    @staticmethod
    def special_value(v):
        """ 特殊值的处理 db在操作update时，value可用sql语法糖来操作，这时不需要对外部value加'' """
        return v if 'concat(' in v and len(v) > 6 and v[:7] == 'concat(' else "'%s'" % v

    @staticmethod
    @func_overtime(0.5)
    def delete(table: str, where: str = None):
        # delete from table where k1=v1,k2=v2
        if bool(DBImpl.execute('DELETE FROM %s%s' % (table, '' if where is None else ' WHERE %s' % where))):
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
    def execute(sql: str, commit=False, result=False, last_row_id=False):
        """ 纯原生执行sql，可在内天马行空的写sql
        :sql sql语句
        :commit 是否提交事务
        :result 是否返回结果 []，todo 需要编写一个方法，生成dict
        :last_row_id 是否返回最近插入的id
        """
        r = DBImpl.execute(sql)
        if result:
            r1 = None if r is None else r.fetchall()
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
            t = DB.retrieve(
                ConstantSql.column_name(
                    table_name,
                    app.config['DATABASE_NAME'])  # todo appConfig中需要增加DATABASE_NAME
            )  # 获取表字段
            if isEmpty(t):
                i('查询表列名出错 %s' % traceback.format_exc())
                raise Exception('查询表列名出错')
            column_names = tuple(s[0] for s in t)

        r = DB.retrieve(sql, fetchone)
        if isEmpty(r):
            return None if fetchone else []
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
            return None if fetchone else []
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
            data.update({column_names[i]: d
            if not (isinstance(d, datetime.datetime) | isinstance(d, datetime.date))
            else int(time.mktime(d.timetuple()))})
        return data


class DBImpl:

    @staticmethod
    def execute(sql):
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
                print(traceback.format_exc())
                return None

    @staticmethod
    def commit():
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


class ConstantSql:

    @staticmethod
    def column_name(table_name, db_name):
        """ 查询表的列名 """
        return "select column_name from information_schema.COLUMNS where table_schema = '%s' and table_name = '%s'" \
               % (db_name, table_name)
