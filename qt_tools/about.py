#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QApplication, QWidget
from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader


class About(QWidget):
    def __init__(self):
        self.ui = QUiLoader().load('about.ui')

    def close_about_page(self):
        self.ui.close()

    def open_page(self):
        self.ui.closeAboutButton.clicked.connect(self.close_about_page)
        self.ui.show()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    about_page = About()
    about_page.open_page()
    app.exec_()
