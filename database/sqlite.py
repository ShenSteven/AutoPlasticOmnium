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


def init_sqlite_database(logger, database_name,table_name='RESULT'):
    """init conf/setting.db, OutPut/result.db"""
    try:
        if not os.path.exists(database_name):
            with Sqlite(database_name) as db:
                db.execute_commit('''CREATE TABLE SHA256_ENCRYPTION
                               (NAME TEXT PRIMARY KEY     NOT NULL,
                               SHA256           TEXT    NOT NULL
                               );''')
                db.execute_commit('''CREATE TABLE COUNT
                                           (NAME TEXT PRIMARY KEY     NOT NULL,
                                           VALUE           INT    NOT NULL
                                           );''')
                db.execute_commit("INSERT INTO COUNT (NAME,VALUE) VALUES ('continue_fail_count', '0')")
                db.execute_commit("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_pass_count', '0')")
                db.execute_commit("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_fail_count', '0')")
                db.execute_commit("INSERT INTO COUNT (NAME,VALUE) VALUES ('total_abort_count', '0')")
                logger.debug(f"setting.db table created successfully")
        if not os.path.exists(gv.database_result):
            with Sqlite(gv.database_result) as db:
                db.execute_commit(f'''CREATE TABLE {table_name}
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
                logger.debug(f"result.db table created successfully")
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

    def execute_commit(self, command):
        # try:
        self.cur.execute(command)
        if not command.startswith('SELECT'):
            self.conn.commit()
        # except Exception as e:
        #     print(e)
            # self.conn.rollback()
