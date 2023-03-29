# # -*- coding: utf-8 -*-
# widget_validation.py

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt


"""
Модуль для проверки/валидности вводимых данных.
"""


class CheckEmptyFields:
    """
    Класс проверки заполенности виджетов/форм данными и соответствующей цветовой индикацией.
    """
    def __init__(self, fields_lst):
        self.fields_lst = fields_lst

    def set_widget_colors(self):
        """
        Заливка цветом при проверке наличия данных.
        :return:
        """
        filling_status = []
        for wgt in self.fields_lst:
            if isinstance(wgt, QtWidgets.QLineEdit):
                if wgt.text() == "":
                    wgt.setStyleSheet("QLineEdit {background: rgb(255, 153, 153); selection-background-color: rgb(233, 99, 0); }")
                    filling_status.append(False)
                else:
                    wgt.setStyleSheet("QLineEdit {background: rgb(255, 255, 255);}")
                    filling_status.append(True)
            elif isinstance(wgt, QtWidgets.QComboBox):
                wgt.setStyleSheet("QComboBox {background-color: rgb(255, 153, 153);}")
            elif isinstance(wgt, QtWidgets.QDateEdit):
                pass
            elif isinstance(wgt, QtWidgets.QCheckBox):
                if wgt.isChecked():
                    wgt.setStyleSheet("QCheckBox::indicator:checked {background-color : white; border: 1px solid black;}")
                    filling_status.append(True)
                else:
                    wgt.setStyleSheet("QCheckBox::indicator:unchecked {background-color: rgb(255, 153, 153); border: 1px solid black;}")
                    filling_status.append(False)
            elif isinstance(wgt, QtWidgets.QTreeWidget):
                if any(item.checkState(0) == QtCore.Qt.Checked for item in wgt.findItems("", Qt.MatchContains | Qt.MatchRecursive)):
                    filling_status.append(True)
                    wgt.setStyleSheet("QLineEdit {background: rgb(255, 255, 255);}")
                else:
                    wgt.setStyleSheet("QTreeWidget {background: rgb(255, 153, 153); selection-background-color: rgb(233, 99, 0); }")
                    filling_status.append(False)
        return filling_status

    def clear_widgets_color(self):
        """
        Очистка заливки виджетов после добавления/сохранения.
        :return:
        """
        for wgt in self.fields_lst:
            if isinstance(wgt, QtWidgets.QLineEdit):
                wgt.setStyleSheet("QLineEdit {background: rgb(255, 255, 255);}")
            elif isinstance(wgt, QtWidgets.QComboBox):
                wgt.setStyleSheet("QComboBox {background-color: rgb(255, 255, 255);}")
            elif isinstance(wgt, QtWidgets.QDateEdit):
                pass
            elif isinstance(wgt, QtWidgets.QCheckBox):
                if wgt.isChecked():
                    wgt.setStyleSheet("QCheckBox::indicator:checked {background-color : white; border: 1px solid black;}")
                else:
                    wgt.setStyleSheet("QCheckBox::indicator:unchecked {background-color: rgb(255, 153, 153); border: 1px solid black;}")
            elif isinstance(wgt, QtWidgets.QTreeWidget):
                wgt.setStyleSheet("QLineEdit {background: rgb(255, 255, 255);}")