#!/usr/bin/env python
# coding: utf-8
"""
@File   : main.py
@Author : Steven.Shen
@Date   : 2022/3/7
@Desc   : 
"""
import sys
from os.path import dirname, abspath, join
from traceback import format_exception
from PyQt5.QtWidgets import QApplication, QMessageBox
import ui.mainform as mf
import runin.rmainform as rmf
import conf.globalvar as gv

# get app dir path
bundle_dir = ''


def get_about(about_abspath):
    """get app about information"""
    about_app = {}
    with open(join(dirname(abspath(__file__)), about_abspath), 'r', encoding='utf-8') as f:
        exec(f.read(), about_app)
    return about_app


def get_app_dir_path():
    global bundle_dir
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print('running in a PyInstaller bundle')
        bundle_dir = sys._MEIPASS
    else:
        print('running in a normal Python process')
        bundle_dir = dirname(abspath(__file__))
    print(bundle_dir)


get_app_dir_path()


def excepthook(cls, exception, traceback):
    # import conf.globalvar as gv
    gv.lg.logger.fatal("".join(format_exception(cls, exception, traceback)))
    QMessageBox.critical(None, "Error", "".join(format_exception(cls, exception, traceback)))


def main():
    sys.excepthook = excepthook
    app = QApplication([])
    print("applicationDirPath:", app.applicationDirPath())
    about_abspath = 'conf/__version__.py'
    try:
        if get_about(about_abspath)['__station__'] == 'RUNIN' or get_about(about_abspath)['__station__'] == 'ORT':
            loginWin = rmf.LoginWind()
            loginWin.ui.show()
        else:
            mainWin = mf.MainForm()
            mainWin.ui.show()

        sys.exit(app.exec_())
    except KeyboardInterrupt:
        # import conf.globalvar as gv
        gv.lg.logger.fatal('KeyboardInterrupt')
        pass


if __name__ == "__main__":
    main()
