# # -*- coding: utf-8 -*-
# app_notifications.py

from PyQt5 import QtCore, QtGui, QtWidgets
from constants.ce_variables import *


class MessageForm(QtWidgets.QDialog):
    """
    Класс интерфейса формы с дополнительными информационными сообщениями.
    """

    def __init__(self, title_txt, accept_btn_txt, reject_btn_txt, message_txt, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title_txt)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.addButton(accept_btn_txt, QtWidgets.QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(reject_btn_txt, QtWidgets.QDialogButtonBox.RejectRole)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.frame_icon_and_message = QtWidgets.QFrame(self)
        self.frame_icon_and_message.setObjectName("frame_icon_and_message")
        self.horizontalLayout_icon_and_message = QtWidgets.QHBoxLayout(self.frame_icon_and_message)
        self.horizontalLayout_icon_and_message.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout_icon_and_message.setSpacing(2)
        self.horizontalLayout_icon_and_message.setObjectName("horizontalLayout_icon_and_message")

        self.label_icon = QtWidgets.QLabel(self.frame_icon_and_message)
        if title_txt == "Внимание!":
            self.label_icon.setPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}error.png"))
        else:
            self.label_icon.setPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}information.png"))

        self.message = QtWidgets.QLabel(self.frame_icon_and_message)
        self.message.setText(message_txt)

        self.horizontalLayout_icon_and_message.addWidget(self.label_icon)
        self.horizontalLayout_icon_and_message.addWidget(self.message)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.frame_icon_and_message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        """
        Ф-я вызываемая при закрытии формы.
        :param event:
        :return:
        """
        event.accept()


class AppStatusBar(QtWidgets.QWidget):
    """
    Класс для сообщений статусбара.
    """

    def __init__(self, parent=None):
        super(AppStatusBar, self).__init__(parent)
        self.parent = parent
        self.window_statusbar = self.parent.statusbar

    def normal_message(self, cur_text):
        """
        Обычное сообщение.
        :param cur_text:
        :return:
        """
        self.window_statusbar.setStyleSheet("background-color : rgb(239, 240, 241); font: bold 14px; color: black;")
        self.window_statusbar.showMessage(f'{cur_text}')

    def green_message(self, cur_text):
        """
        Зеленое сообщение.
        :param cur_text:
        :return:
        """
        self.window_statusbar.setStyleSheet("background-color : green; font: bold 14px; color: white;")
        self.window_statusbar.showMessage(f'{cur_text}')

    def yellow_message(self, cur_text):
        """
        Жёлтое сообщение.
        :param cur_text:
        :return:
        """
        self.window_statusbar.setStyleSheet("background-color : yellow; font: bold 14px; color: black;")
        self.window_statusbar.showMessage(f'{cur_text}')

    def red_message(self, cur_text):
        """
        Красное сообщение.
        :param cur_text:
        :return:
        """
        self.window_statusbar.setStyleSheet("background-color : red; font: bold 14px; color: white;")
        self.window_statusbar.showMessage(f'{cur_text}')

    def clear_statusbar(self):
        """
        Очистка статусбара от предыдущего сообщения.
        :return:
        """
        self.window_statusbar.setStyleSheet("background-color : rgb(239, 240, 241); font: bold 14px; color: black;")
        self.window_statusbar.clearMessage()

