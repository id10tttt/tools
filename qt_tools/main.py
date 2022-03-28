#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader
from compute_day import ComputeTools
from about import About
from guess_game import GuessNumberGame


class MainTools:
    def __init__(self):
        self.ui = QUiLoader().load('main.ui')


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    main_tool = MainTools()
    about_page = About()
    compute_page = ComputeTools()
    guess_number_game = GuessNumberGame()
    main_tool.ui.show()
    # connect button
    main_tool.ui.computeDayButton.clicked.connect(compute_page.open_page)
    main_tool.ui.guessNumberButton.clicked.connect(guess_number_game.initial_page)
    # triggered action
    main_tool.ui.actionAbout.triggered.connect(about_page.open_page)

    app.exec_()
