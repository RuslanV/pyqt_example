# -*- coding: utf-8 -*-
# table_models.py

from PyQt5.QtCore import QAbstractTableModel, Qt
import datetime as dt
from constants.ce_variables import *


'''
Модели данных для вывода инфомции во вьюхах
'''


class PandasTableModelHH(QAbstractTableModel):
    '''
    Класс модели данных (из датафрейма pandas) в виде простой таблицы с горизонтальными заголовками (с названиями колонок).
    '''
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role):
        if index.isValid:
            if role == Qt.DisplayRole:
                value = self._data.iloc[index.row(), index.column()]
                if isinstance(value, dt.date):
                    return value.strftime("%d.%m.%Y")
                return str(self._data.iloc[index.row(), index.column()])
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self._data.columns[col])
        return None


class PandasTableModelVH(QAbstractTableModel):
    '''
    Класс модели данных (из датафрейма pandas) в виде простой таблицы с вертикальными заголовками (с названиями строк).
    '''
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.columns.size

    def columnCount(self, parent=None):
        return len(self._data.values)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data[list(self._data.columns.values)[index.row()]][index.column()]
            if isinstance(value, dt.date):
                return value.strftime("%d.%m.%Y")
            if isinstance(value, dt.date):
                return value.strftime("%d.%m.%Y")
            if isinstance(value, float):
                return "%.2f" % value
            if isinstance(value, str):
                return f"{value}"
            return value
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft

    def headerData(self, col, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            pass
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(self._data.columns[col])
