#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox
from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader


class GuessNumberGame(QWidget):
    def __init__(self):
        self.ui = QUiLoader().load('guess_number.ui')
        self.initial_number = random.randint(1, 101)
        self.last_bigger_number = 100
        self.last_smaller_number = 1

    def restart_guess_game(self):
        self.initial_number = random.randint(1, 101)
        self.ui.notificationLabel.setText('Shall we? Let\'s dance *_*')
        self.ui.guessNumberEdit.clear()
        self.ui.textBrowser.clear()
        self.last_bigger_number = 100
        self.last_smaller_number = 1

    def guess_win_or_lose(self):
        guess_number = self.ui.guessNumberEdit.text()
        if not guess_number:
            return True

        try:
            if not guess_number:
                guess_number = 0
            guess_number = int(guess_number)
        except Exception as e:
            self.msg_notifaction(e)

        if guess_number > self.initial_number and guess_number > self.last_bigger_number:
            self.ui.notificationLabel.setText(
                '搞这么大干啥: {}\n介于： {} ～ {} 好不好'.format(guess_number, self.last_smaller_number, self.last_bigger_number))
            self.ui.textBrowser.append(str(guess_number))
        elif self.initial_number < guess_number < self.last_bigger_number:
            self.last_bigger_number = guess_number
            self.ui.notificationLabel.setText(
                '搞这么大干啥: {}\n介于： {} ～ {} 好不好'.format(guess_number, self.last_smaller_number, self.last_bigger_number))
        elif guess_number < self.initial_number and guess_number < self.last_smaller_number:
            self.ui.notificationLabel.setText(
                '啧啧啧，这么小: {}\n介于： {} ～ {} 好不好'.format(guess_number, self.last_smaller_number, self.last_bigger_number))
            self.ui.textBrowser.append(str(guess_number))
        elif self.last_smaller_number < guess_number < self.initial_number:
            self.last_smaller_number = guess_number
            self.ui.notificationLabel.setText(
                '啧啧啧，这么小: {}\n介于： {} ～ {} 好不好'.format(guess_number, self.last_smaller_number, self.last_bigger_number))
            self.ui.textBrowser.append(str(guess_number))
        elif guess_number == self.initial_number:
            self.ui.notificationLabel.setText('哦哟哦哟，牛逼: {}'.format(guess_number))
            self.ui.textBrowser.append(str(guess_number))
        else:
            self.ui.notificationLabel.setText('Ooooooppps')

    def msg_notifaction(self, err_msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText('不要乱输，谢谢 >_<')
        msg_box.setDetailedText('错误信息: {}'.format(err_msg))
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.show()
        msg_box.exec()

    def initial_page(self):
        self.ui.restartGameButton.clicked.connect(self.restart_guess_game)
        # self.ui.guessNumberEdit.textChanged.connect(self.guess_win_or_lose)
        self.ui.connect(self.ui.guessNumberEdit, QtCore.SIGNAL("returnPressed()"), self.guess_win_or_lose)
        self.ui.show()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    guess_game = GuessNumberGame()
    guess_game.initial_page()
    app.exec_()
