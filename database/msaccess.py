#!/usr/bin/env python
# coding: utf-8
"""
@File   : msaccess.py
@Author : Steven.Shen
@Date   : 4/10/2023
@Desc   : 
"""
# !/usr/bin/env python
# coding: utf-8
"""
@File   : mysql.py
@Author : Steven.Shen
@Date   : 4/10/2023
@Desc   : 
"""
import pyodbc


class MSAccess(object):
    def __init__(self, path_db):
        self.conn = pyodbc.connect(
            (r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + path_db + ";Uid=;Pwd=;charset='utf-8';"))
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exec_type, value, traceback):
        self.cursor.close()
        self.conn.close()

    def select_all(self, sql):  # 查询sql语句返回的所有数据
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def select_one(self, sql):  # 查询sql语句返回的一条数据
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def select_many(self, sql, num):  # 查询sql语句返回的几条数据
        self.cursor.execute(sql)
        return self.cursor.fetchmany(num)

    def execute_commit(self, command):
        try:
            self.cursor.execute(command)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()


if __name__ == '__main__':
    pass
