# -*- coding: utf-8 -*-
# overridden_threads_classes.py

from PyQt5 import QtCore, QtGui, QtWidgets
from constants.ce_variables import *
import traceback


class GetDataThreadNew(QtCore.QThread):
    """
    Класс собственных потоков для выгрузки данных из БД.
    Для контроля потоков используется очередь.
    """
    task_done = QtCore.pyqtSignal(object, name='taskDone')

    def __init__(self, id, queue, current_func, current_val=None, currnt_mode=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.id = id
        self.queue = queue
        self.current_func = current_func
        self.current_val = current_val
        self.currnt_mode = currnt_mode

    def run(self):
        self.queue.get(True)
        self.result = self.current_func(self.current_val, self.currnt_mode)
        self.task_done.emit(self.result)
        self.queue.task_done()

    def stop(self):
        try:
            self.running = False
            self.terminate()
        except Exception as _err:
            err_msg = f"{traceback.format_exc()} - Ошибка: {_err}"
            logging.error(err_msg)
getdata_thread = {}


class WriteDataThreadNew(QtCore.QThread):
    """
    Класс собственных потоков для записи/обновления/удаления в БД.
    Для контроля потоков используется очередь
    Без сигнала.
    """

    def __init__(self, id, queue, current_func, current_val=None, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.id = id
        self.queue = queue
        self.current_func = current_func
        self.current_val = current_val

    def run(self):
        self.queue.get(True)
        self.current_func(self.current_val)
        self.queue.task_done()

    def stop(self):
        try:
            self.running = False
            self.terminate()
        except Exception as _err:
            err_msg = f"{traceback.format_exc()} - Ошибка: {_err}"
            logging.error(err_msg)
writedata_thread = {}
