from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMessageBox, QAbstractItemView, QStyleFactory
from PySide2.QtUiTools import QUiLoader
from model.testcase import *
from conf import globalvar as gv


#
# def run(is_cyclic=False, single_step=True):
#     test_task = TestCase(r"F:\pyside2\scripts\fireflyALL.xlsx", 'MBLT')
#
#     if is_cyclic:
#         while True:
#             test_task.run(test_task.test_suites.copy(), True, 0)
#     elif single_step:
#         test_task.test_suites.copy()[0].test_steps[2].run()
#     else:
#         create_csv_file('result.csv', ['No', 'Phase test_name', 'Test test_name', 'Error Code'])
#         test_task.run(test_task.test_suites.copy(), True)
#         print(gv.csv_list_result)
#         write_csv_file('result.csv', gv.csv_list_result)
#         write_csv_file('result.csv', gv.csv_list_header)


# run(False)


class MainForm:
    def __init__(self):
        self.ui = QUiLoader().load('ui/main.ui')
        self.ui.treeView.setModel(QtGui.QStandardItemModel())
        self.model = self.ui.treeView.model()
        self.test_task = TestCase("scripts/fireflyALL.xlsx", 'MBLT')
        self.create_model(self.test_task.test_suites)
        self.model.itemChanged.connect(self.handle_treeItemChanged)
        # self.ui.treeView.clicked.connect(self.handle_click)

        # self.ui.treeView.selectionModel().currentChanged.connect(self.onCurrentChanged)

    def handle_treeItemChanged(self, checked_item):
        if gv.startFlag:
            return
        if checked_item.parent() is None:
            pNo = checked_item.row()
            cc=True if checked_item.checkState() == Qt.Checked else False
            self.test_task.test_suites[pNo].isTest = True if checked_item.checkState() == Qt.Checked else False
            # self.model.itemChanged.disconnect()
            ss = checked_item.childCount()
            QMessageBox.about(self.ui, "!!", str(ss))
            # ss = checked_item.parent()

        # state = checked_item.checkState()
        # indices = self.ui.treeView.selectedIndexes()
        # for idx in indices:
        #     item = idx.model().itemFromIndex(idx)
        #     item.setCheckState(state)
        # QMessageBox.about(self.ui, "!!", ss)

    def onCurrentChanged(self, current, previous):
        txt = '父级:[{}] '.format(str(current.parent().data()))
        txt += '当前选中:[(行{},列{})] '.format(current.row(), current.column())

        name = ''
        info = ''
        if current.column() == 0:
            name = str(current.data())
            info = str(current.sibling(current.row(), 1).data())
        else:
            name = str(current.sibling(current.row(), 0).data())
            info = str(current.data())

        txt += '名称:[{}]  信息:[{}]'.format(name, info)

        self.ui.statusBar().showMessage(txt)

    def create_model(self, sequences):
        self.model.clear()
        self.ui.treeView.sortByColumn(0, QtCore.Qt.AscendingOrder)
        for i, suite in enumerate(sequences):
            root = []
            root_node = QtGui.QStandardItem()
            root_node.setData(f'{suite.index + 1}. {suite.SeqName}', role=QtCore.Qt.DisplayRole)
            root_node.setIcon(QIcon('images/close.png'))
            root_node.setCheckable(True)
            root_node.setBackground(Qt.red)
            root.append(root_node)
            for step in suite.test_steps:
                steps = []
                step_node = QtGui.QStandardItem()
                step_node.setData(f'{step.index}) {step.ItemName}', role=QtCore.Qt.DisplayRole)
                step_node.setCheckable(True)
                step_node.setIcon(QIcon('images/stop.png'))
                step_node.setBackground(Qt.green)
                steps.append(step_node)
                root_node.appendRow(steps)
            self.model.appendRow(root)
        self.ui.treeView.setStyle(QStyleFactory.create('windows'))  # 设置成有虚线连接的方式
        self.ui.treeView.expandAll()
        self.ui.treeView.resizeColumnToContents(0)

    def handle_click(self):
        QMessageBox.about(self.ui,
                          '统计结果',
                          f'''薪资20000 以上的有：\n
                    \n薪资20000 以下的有：\n'''
                          )


app = QApplication([])
mainForm = MainForm()
mainForm.ui.show()
app.exec_()

# def handleCalc(self):
#     info = self.ui.textEdit.toPlainText()
#
#     salary_above_20k = ''
#     salary_below_20k = ''
#     for line in info.splitlines():
#         if not line.strip():
#             continue
#         parts = line.split(' ')
#
#         parts = [p for p in parts if p]
#         name, salary, age = parts
#         if int(salary) >= 20000:
#             salary_above_20k += name + '\n'
#         else:
#             salary_below_20k += name + '\n'
#
#     QMessageBox.about(self.ui,
#                       '统计结果',
#                       f'''薪资20000 以上的有：\n{salary_above_20k}
#                 \n薪资20000 以下的有：\n{salary_below_20k}'''
#                       )
