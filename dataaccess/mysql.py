#!/usr/bin/env python
# coding: utf-8
"""
@File   : mysql.py
@Author : Steven.Shen
@Date   : 4/10/2023
@Desc   : 
"""
from inspect import currentframe

import pymysql


# mysql_connect_config = {
#     "host": "127.0.0.1",
#     "port": 3307,
#     "database": "lebo",
#     "charset": "utf8",
#     "user": "root",
#     "passwd": "root"
# }

def init_mysql_database(logger, database_name, table_name='RESULT'):
    """init local mysql database"""
    try:
        with MySQL(host='127.0.0.1', port=3306, user='root', passwd='123456') as db:
            db.execute_commit(f'''CREATE DATABASE {database_name};''')
            db.execute_commit(f'''USE {database_name};''')
            db.execute_commit(f'''CREATE TABLE {table_name}
                                                 (ID            INTEGER PRIMARY KEY AUTO_INCREMENT,
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
            logger.debug(f"MySQL database and table created successfully")
    except Exception as e:
        logger.fatal(f'{currentframe().f_code.co_name}:{e},{database_name}')


class MySQL(object):
    def __init__(self, **configs):
        self.conn = pymysql.connect(**configs)
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
            print(e)
            self.conn.rollback()


if __name__ == '__main__':
    with MySQL(host='127.0.0.1', port=3306, user='root', passwd='123456') as mydb:
        mydb.execute_commit('''CREATE DATABASE AutoPlasticOmnium;''')
        mydb.execute_commit('''USE AutoPlasticOmnium;''')
        mydb.execute_commit('''CREATE TABLE RESULT
                                     (ID            INTEGER PRIMARY KEY AUTO_INCREMENT,
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
        # mydb.execute_commit(f'''INSERT INTO RESULT
        #               (ID,SN,STATION_NAME,STATION_NO,MODEL,SUITE_NAME,ITEM_NAME,SPEC,LSL,VALUE,USL,
        #               ELAPSED_TIME,ERROR_CODE,ERROR_DETAILS,START_TIME,TEST_RESULT,STATUS)
        #               VALUES (NULL,'{test_case.myWind.SN}','{gv.cf.station.station_name}','{gv.cf.station.station_no}',
        #               '{test_case.myWind.dut_model}','{self.SuiteName}','{self.StepName}','{self.SPEC}','{self.LSL}',
        #               '{self.testValue}','{self.USL}',{self.elapsedTime},'{self.error_code}','{self.error_details}',
        #               '{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}','{test_result}','{self.status}')
        #               ''')
