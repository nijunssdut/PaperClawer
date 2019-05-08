# -*- coding:utf-8 -*-
import pymysql
import Settings


# 数据库交互相关方法
class dbIO():
    def __init__(self, dbStr=Settings.dbStr):
        self.conn = pymysql.connect(host=Settings.hostStr, user=Settings.userStr,
                                    passwd=Settings.pwdStr, db=dbStr, charset='utf8')
        self.cur = self.conn.cursor()

    def __del__(self):
        # self.cur.close()
        self.conn.close()

    def count(self, sql):
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(sql)
            return self.cur.rowcount
        except Exception as e:
            print(str(e))
            return 0
        finally:
            self.cur.close()

    def save(self, sql):
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(sql)
            self.conn.commit()
            return 1
        except Exception as e:
            print(str(e))
            return 0
        finally:
            self.cur.close()

    def load(self, sql):
        try:
            self.cur = self.conn.cursor()
            self.cur.execute(sql)
            return self.cur.fetchall()
        except Exception as e:
            print(str(e))
            return 0
        finally:
            self.cur.close()



