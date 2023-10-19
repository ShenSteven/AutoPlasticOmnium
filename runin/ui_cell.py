# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_cell.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_cell(object):
    def setupUi(self, cell):
        cell.setObjectName("cell")
        cell.resize(236, 110)
        cell.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        cell.setStyleSheet("background-color: rgb(209, 209, 209);")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(cell)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame = QtWidgets.QFrame(cell)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lb_cellNum = QtWidgets.QLabel(self.frame)
        self.lb_cellNum.setMinimumSize(QtCore.QSize(28, 17))
        self.lb_cellNum.setStyleSheet("background-color: rgb(189, 189, 189);")
        self.lb_cellNum.setTextFormat(QtCore.Qt.AutoText)
        self.lb_cellNum.setScaledContents(False)
        self.lb_cellNum.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_cellNum.setObjectName("lb_cellNum")
        self.horizontalLayout.addWidget(self.lb_cellNum)
        self.lb_sn = QtWidgets.QLabel(self.frame)
        self.lb_sn.setMinimumSize(QtCore.QSize(135, 21))
        self.lb_sn.setTextFormat(QtCore.Qt.AutoText)
        self.lb_sn.setScaledContents(False)
        self.lb_sn.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_sn.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.lb_sn.setObjectName("lb_sn")
        self.horizontalLayout.addWidget(self.lb_sn)
        self.horizontalLayout.setStretch(0, 10)
        self.horizontalLayout.setStretch(1, 90)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.lb_testName = QtWidgets.QLabel(self.frame)
        self.lb_testName.setMinimumSize(QtCore.QSize(210, 24))
        self.lb_testName.setStyleSheet("")
        self.lb_testName.setTextFormat(QtCore.Qt.AutoText)
        self.lb_testName.setScaledContents(False)
        self.lb_testName.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_testName.setObjectName("lb_testName")
        self.verticalLayout.addWidget(self.lb_testName)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(1, -1, 1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lb_model = QtWidgets.QLabel(self.frame)
        self.lb_model.setMinimumSize(QtCore.QSize(51, 20))
        self.lb_model.setTextFormat(QtCore.Qt.AutoText)
        self.lb_model.setScaledContents(False)
        self.lb_model.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_model.setObjectName("lb_model")
        self.horizontalLayout_2.addWidget(self.lb_model)
        self.lb_testTime = QtWidgets.QLabel(self.frame)
        self.lb_testTime.setMinimumSize(QtCore.QSize(81, 21))
        self.lb_testTime.setTextFormat(QtCore.Qt.AutoText)
        self.lb_testTime.setScaledContents(False)
        self.lb_testTime.setAlignment(QtCore.Qt.AlignCenter)
        self.lb_testTime.setObjectName("lb_testTime")
        self.horizontalLayout_2.addWidget(self.lb_testTime)
        self.lbl_failCount = QtWidgets.QLabel(self.frame)
        self.lbl_failCount.setMinimumSize(QtCore.QSize(31, 21))
        self.lbl_failCount.setTextFormat(QtCore.Qt.AutoText)
        self.lbl_failCount.setScaledContents(False)
        self.lbl_failCount.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_failCount.setObjectName("lbl_failCount")
        self.horizontalLayout_2.addWidget(self.lbl_failCount)
        self.horizontalLayout_2.setStretch(0, 20)
        self.horizontalLayout_2.setStretch(1, 70)
        self.horizontalLayout_2.setStretch(2, 10)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.horizontalLayout_4.addWidget(self.frame)

        self.retranslateUi(cell)
        QtCore.QMetaObject.connectSlotsByName(cell)

    def retranslateUi(self, cell):
        _translate = QtCore.QCoreApplication.translate
        cell.setWindowTitle(_translate("cell", "Form"))
        self.lb_cellNum.setText(_translate("cell", "80"))
        self.lb_sn.setText(_translate("cell", "NA5F004BE8DNNX42"))
        self.lb_testName.setText(_translate("cell", "CPUStressTest"))
        self.lb_model.setText(_translate("cell", "leaf"))
        self.lb_testTime.setText(_translate("cell", "00:00:00"))
        self.lbl_failCount.setText(_translate("cell", "1"))
