# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'download.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.download_link_label = QtWidgets.QLabel(self.centralwidget)
        self.download_link_label.setGeometry(QtCore.QRect(50, 50, 66, 19))
        self.download_link_label.setObjectName("download_link_label")
        self.download_url_input = QtWidgets.QLineEdit(self.centralwidget)
        self.download_url_input.setGeometry(QtCore.QRect(130, 40, 611, 36))
        self.download_url_input.setObjectName("download_url_input")
        self.download_file_name = QtWidgets.QLabel(self.centralwidget)
        self.download_file_name.setGeometry(QtCore.QRect(50, 110, 66, 19))
        self.download_file_name.setObjectName("download_file_name")
        self.download_file_name_input = QtWidgets.QLineEdit(self.centralwidget)
        self.download_file_name_input.setGeometry(QtCore.QRect(130, 100, 611, 36))
        self.download_file_name_input.setObjectName("download_file_name_input")
        self.download_file_path = QtWidgets.QLabel(self.centralwidget)
        self.download_file_path.setGeometry(QtCore.QRect(50, 180, 66, 19))
        self.download_file_path.setObjectName("download_file_path")
        self.download_file_path_input = QtWidgets.QLineEdit(self.centralwidget)
        self.download_file_path_input.setGeometry(QtCore.QRect(130, 170, 611, 36))
        self.download_file_path_input.setObjectName("download_file_path_input")
        self.download_progress = QtWidgets.QProgressBar(self.centralwidget)
        self.download_progress.setGeometry(QtCore.QRect(130, 450, 611, 23))
        self.download_progress.setProperty("value", 0)
        self.download_progress.setObjectName("download_progress")
        self.download_progress_label = QtWidgets.QLabel(self.centralwidget)
        self.download_progress_label.setGeometry(QtCore.QRect(50, 450, 66, 19))
        self.download_progress_label.setObjectName("download_progress_label")
        self.start_download_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_download_button.setGeometry(QtCore.QRect(520, 510, 103, 36))
        self.start_download_button.setObjectName("start_download_button")
        self.download_list_table = QtWidgets.QTableView(self.centralwidget)
        self.download_list_table.setGeometry(QtCore.QRect(130, 220, 611, 192))
        self.download_list_table.setObjectName("download_list_table")
        self.button_open_folder = QtWidgets.QPushButton(self.centralwidget)
        self.button_open_folder.setGeometry(QtCore.QRect(670, 170, 71, 36))
        self.button_open_folder.setObjectName("button_open_folder")
        self.max_async_count_label = QtWidgets.QLabel(self.centralwidget)
        self.max_async_count_label.setGeometry(QtCore.QRect(60, 520, 51, 19))
        self.max_async_count_label.setObjectName("max_async_count_label")
        self.max_async_count_input = QtWidgets.QLineEdit(self.centralwidget)
        self.max_async_count_input.setGeometry(QtCore.QRect(130, 510, 91, 36))
        self.max_async_count_input.setObjectName("max_async_count_input")
        self.button_merge_ts_to_mp4 = QtWidgets.QPushButton(self.centralwidget)
        self.button_merge_ts_to_mp4.setGeometry(QtCore.QRect(640, 510, 103, 36))
        self.button_merge_ts_to_mp4.setObjectName("button_merge_ts_to_mp4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "文件下载"))
        self.download_link_label.setText(_translate("MainWindow", "下载链接"))
        self.download_file_name.setText(_translate("MainWindow", "文件名字"))
        self.download_file_path.setText(_translate("MainWindow", "文件路径"))
        self.download_progress_label.setText(_translate("MainWindow", "下载进度"))
        self.start_download_button.setText(_translate("MainWindow", "开始下载"))
        self.button_open_folder.setText(_translate("MainWindow", "打开"))
        self.max_async_count_label.setText(_translate("MainWindow", "协程数"))
        self.max_async_count_input.setText(_translate("MainWindow", "128"))
        self.button_merge_ts_to_mp4.setText(_translate("MainWindow", "合并"))
