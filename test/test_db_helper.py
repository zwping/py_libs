
from db_helper import DBHelper


# 测试用例 本地数据库及表准备
"""
CREATE TABLE `test` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
"""
db = DBHelper().init_conn_pool('127.0.0.1', 3306, 'root', '123456', 'test', 'utf8')


def test_db_增():
    with db.getconn() as conn:
        for s in 'python':
            sql = "insert into `test` (`name`) values (%s)"
            assert conn.execute(sql, s) == 1
        conn.commit()
        sql = 'select count(`id`) from `test`'
        assert conn.execute(sql) != -1
        d = conn.fetchone()
        print(d)
        import time
        print(int(time.time()))
        assert d['count(`id`)'] >= 10


def test_db_删():
    with db.getconn() as conn:
        assert conn.execute("insert into `test` (`name`) values ('测试')") == 1
        conn.commit()
        last_id = conn.lastrowid()
        sql = 'delete from `test` where `id`=%s'
        assert conn.execute(sql, last_id) == 1
        conn.commit()


def test_db_改():
    with db.getconn() as conn:
        assert conn.execute("insert into `test` (`name`) values ('测试')") == 1
        conn.commit()
        last_id = conn.lastrowid()
        sql = 'update `test` set `name`=%s where `id`=%s'
        assert conn.execute(sql, ('修改后的值', last_id)) == 1
        conn.commit()
        assert conn.execute('select `name` from `test` where `id`=%s', last_id) != -1
        d = conn.fetchone()
        print(d)
        assert d['name'] == '修改后的值'

def test_db_查():
    with db.getconn() as conn:
        assert conn.execute("insert into `test` (`name`) values ('测试')") == 1
        assert conn.execute("insert into `test` (`name`) values ('测试')") == 1
        assert conn.execute("insert into `test` (`name`) values ('测试')") == 1
        conn.commit()
        assert conn.execute('select * from `test` order by `id` desc') > 3
        for d in conn.fetchall()[0:3]:
            print(d)
            assert d['name'] == '测试'

