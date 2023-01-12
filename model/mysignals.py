#!/usr/bin/env python
# coding: utf-8
"""
@File   : mysignals.py
@Author : Steven.Shen
@Date   : 1/11/2023
@Desc   : 
"""
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtWidgets import QLabel, QAction


class MySignals(QObject):
    """自定义信号类"""
    loadseq = pyqtSignal(str)
    update_tableWidget = pyqtSignal((list,), (str,))
    updateLabel = pyqtSignal([QLabel, str, int, QBrush], [QLabel, str, int], [QLabel, str])
    treeWidgetColor = pyqtSignal([QBrush, int, int, bool])
    timingSignal = pyqtSignal(bool)
    textEditClearSignal = pyqtSignal(str)
    lineEditEnableSignal = pyqtSignal(bool)
    setIconSignal = pyqtSignal(QAction, QIcon)
    updateStatusBarSignal = pyqtSignal(str)
    updateActionSignal = pyqtSignal([QAction, QIcon, str], [QAction, QIcon])
    saveTextEditSignal = pyqtSignal(str)
    controlEnableSignal = pyqtSignal(QAction, bool)
    threadStopSignal = pyqtSignal(str)
    updateConnectStatusSignal = pyqtSignal(bool, str)
    showMessageBox = pyqtSignal([str, str, int])
