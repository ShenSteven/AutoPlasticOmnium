#!/usr/bin/env python
# coding: utf-8
"""
@File   : sqlite.py
@Author : Steven.Shen
@Date   : 2021/12/14
@Desc   : 
"""
import os
import sqlite3
import conf.globalvar as gv
from inspect import currentframe


def init_database(logger, database_name):
    """init conf/setting.db, OutPut/result.db"""
    try:
        if not os.path.exists(database_name):
            with Sqlite(database_name) as db:
                db.execute('''CREATE TABLE SHA256_ENCRYPTION
                               (NAME TEXT PRIMARY KEY     NOT NULL,
                               SHA256           TEXT    NOT NULL
                               );''')
                db.execute('''CREATE TABLE COUNT
                                           (NAME TEXT PRIMARY KEY     NOT NULL,
                                           VALUE           INT    NOT NULL
                                           );''')
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('continue_fail_count', '0')")
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_pass_count', '0')")
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_fail_count', '0')")
                db.execute("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_abort_count', '0')")
                logger.debug(f"Table created successfully")
                print(f"Table created successfully")
        if not os.path.exists(gv.database_result):
            with Sqlite(gv.database_result) as db:
                db.execute('''CREATE TABLE RESULT
                                             (ID            INTEGER PRIMARY KEY AUTOINCREMENT,
                                              SN            TEXT,
                                              STATION_NAME  TEXT    NOT NULL,
                                              STATION_NO    TEXT    NOT NULL,
                                              MODEL         TEXT    NOT NULL,
                                              SUITE_NAME    TEXT    NOT NULL,
                                              ITEM_NAME     TEXT    NOT NULL,
                                              SPEC          TEXT,
                                              LSL           TEXT,
                                              VALUE         TEXT,
                                              USL           TEXT,
                                              ELAPSED_TIME  INT,
                                              ERROR_CODE    TEXT,
                                              ERROR_DETAILS TEXT,
                                              START_TIME    TEXT    NOT NULL,
                                              TEST_RESULT   TEXT    NOT NULL,
                                              STATUS        TEXT    NOT NULL
                                             );''')
                logger.debug(f"Table created successfully")
                print(f"Table created successfully")
    except Exception as e:
        logger.fatal(f'{currentframe().f_code.co_name}:{e},{database_name}')


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
