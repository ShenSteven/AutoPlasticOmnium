#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2022/3/7
@Desc   : 
"""
import sys
from os.path import dirname, abspath
from traceback import format_exception
from PyQt5.QtWidgets import QApplication, QMessageBox
import bll.mainform as mf
import runin.rmainform as rmf
import conf.globalvar as gv

# get app dir path
bundle_dir = ''


def get_app_dir_path():
    global bundle_dir
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # print('running in a PyInstaller bundle')
        bundle_dir = sys._MEIPASS
    else:
        # print('running in a normal Python process')
        bundle_dir = dirname(abspath(__file__))
    # print(bundle_dir)


get_app_dir_path()


def excepthook(cls, exception, traceback):
    gv.lg.logger.fatal("".join(format_exception(cls, exception, traceback)))
    QMessageBox.critical(None, "Error", "".join(format_exception(cls, exception, traceback)))


def main():
    sys.excepthook = excepthook
    app = QApplication([])
    # try:
    #     import qdarkgraystyle
    #     app.setStyleSheet(qdarkgraystyle.load_stylesheet_pyqt5())
    #     print(qdarkgraystyle.load_stylesheet_pyqt5())
    # except:
    #     pass
    try:
        if gv.cfg.RUNIN.IsRUNIN:
            gv.LoginWin = rmf.LoginWind()
            gv.LoginWin.show()
        else:
            gv.MainWin = mf.MainForm()
            gv.MainWin.show()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        gv.lg.logger.fatal('KeyboardInterrupt')


if __name__ == "__main__":
    main()
