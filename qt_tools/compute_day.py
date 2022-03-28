#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import time
import random
import decimal
from PySide2.QtWidgets import QApplication, QMessageBox, QWidget
from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader
from PyQt5.QtCore import QTimer

marry_date = '2020-07-06'
birth_date = '2022-01-22 11:01'
birth_datetime = datetime.datetime.strptime(birth_date, '%Y-%m-%d %H:%M')
marry_datetime = datetime.datetime.strptime(marry_date, '%Y-%m-%d')


def decimal_float_number(number):
    decimal.getcontext().rounding = "ROUND_HALF_UP"
    res = decimal.Decimal(str(number)).quantize(decimal.Decimal("0.00"))
    return str(res)


def format_date(input_date):
    return datetime.datetime.strptime(input_date, '%Y-%m-%d')


def format_datetime(input_date):
    return datetime.datetime.strptime(input_date, '%Y-%m-%d %H:%M')


class ComputeTools(QWidget):
    def __init__(self):
        self.ui = QUiLoader().load('compute_day.ui')
        self.timer = QTimer()
        self.timer.timeout.connect(self.compute_day_second)

    def compute_day_second(self):
        input_date = self.ui.dateEdit.text()
        input_date = format_date(input_date)
        compute_second = datetime.datetime.now().timestamp() - input_date.timestamp()
        compute_day = decimal_float_number(compute_second / 3600 / 24)
        self.ui.secondEdit.setText(str(compute_second))
        self.ui.dayEdit.setText(str(compute_day))

    def msg_notifaction(self, compute_day, compute_second):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText('{}秒, {}天'.format(compute_second, compute_day))
        msg_box.setDetailedText('{}秒, {}天'.format(compute_second, compute_day))
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.show()
        msg_box.exec()

    def compute_realtime_day_second(self):
        self.timer.start(random.randint(10, 1000))
        self.ui.computeRealtime.setEnabled(False)

    def stop_realtime_compute(self):
        self.timer.stop()
        self.ui.computeRealtime.setEnabled(True)

    def open_page(self):
        self.ui.computeRealtime.clicked.connect(self.compute_realtime_day_second)
        self.ui.stopCompute.clicked.connect(self.stop_realtime_compute)
        self.ui.show()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    qt_tools = ComputeTools()
    qt_tools.open_page()
    app.exec_()
