#!/usr/bin/env python
# coding: utf-8
"""
@File   : sqlite.py
@Author : Steven.Shen
@Date   : 2021/12/14
@Desc   : 
"""
import sqlite3


class Sqlite(object):
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exec_type, value, traceback):
        self.cur.close()
        self.conn.close()

    def execute(self, command):
        self.cur.execute(command)
        self.conn.commit()
