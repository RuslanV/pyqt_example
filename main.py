# -*- coding: utf-8 -*-

import sys
import datetime as dt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QSplashScreen, QSpacerItem, QTabBar, QProgressBar, QSplitter, QHeaderView
from PyQt5.QtGui import QIcon, QMovie, QPixmap, QCursor, QPalette, QColor
from PyQt5.QtCore import Qt, QEvent, pyqtSlot
import ui_files.main_gui as main_gui
import ui_files.EQ_INFO_GUI as EQ_INFO_GUI
import queue
from constants.ce_variables import *
from modules.overridden_threads_classes import *
from modules.app_notifications import *
from modules.sql_orm_conn import *
from modules.widget_validation import *
from models.table_models import PandasTableModelHH, PandasTableModelVH


"""
Пример многопоточного приложения (DEMO APP) с базовым модулем учёта измерительного оборудования для различных лабораторий (химических/строительныйх и т.п.).
Данный модуль явлется моей разработкой - Шаповалов Р.В. и входит в состав комлексной системы СЭД (также собственная разработка), 
позволяющей управлять документами и различными процессами на предприятии химической/строительной отрасли в соответствии со стандартом ISO 9000.
"""


def find_checked_test_methods(tree_widget):
    """
    Ф-я нахождения родительских/дочерних отмеченных элементов дерева,
    методы испытания для оборудования
    :param tree_widget: принимаемый виджет-дерево
    :return: список названий методов испытаний (выбранных)
    """
    checked_lst = []
    for item in tree_widget.findItems("", Qt.MatchContains | Qt.MatchRecursive):
        if item.checkState(0) == QtCore.Qt.Checked:
            checked_lst.append(item.text(0))
    return checked_lst


def check_patfile(current_path_to_file=None):
    """
    Вспомогательная ф-я для проверки что файл существует.
    :param current_path_to_file:
    :return:
    """
    if os.path.isfile(current_path_to_file):
        return True
    else:
        return False


def get_value_from_fields(wigdet_arr):
    """
    Вспомогательная ф-я извлечения значений из полей различных виджетов
    :param data_arr: массив виджетов
    :return: значения из виджетов
    """
    result_data_list = []
    for wgt in wigdet_arr:
        if isinstance(wgt, QtWidgets.QLineEdit):
            if "_file" in wgt.objectName():
                currnt_file = wgt.text()
                if currnt_file != "" and check_patfile(currnt_file):
                    file_data = None
                    result_data_list.append(file_data)
                else:
                    result_data_list.append(None)
                    result_data_list.append(None)
            else:
                result_data_list.append(wgt.text())
        elif isinstance(wgt, QtWidgets.QComboBox):
            result_data_list.append(wgt.currentText())
        elif isinstance(wgt, QtWidgets.QDateEdit):
            result_data_list.append(wgt.date().toString(Qt.ISODate))
        elif isinstance(wgt, QtWidgets.QTreeWidget):
            checked_tree_items = find_checked_test_methods(wgt)
            checked_tree_items = ", ".join(checked_tree_items)
            result_data_list.append(checked_tree_items)
        else:
            result_data_list.append(None)
    return result_data_list


def initialisation_required_fields(current_fields):
    """
    Ф-я инициализации обязательных к заполнению полей
    :return:
    """
    required_to_fill_fields = []
    for wgt in current_fields:
        if isinstance(wgt, QtWidgets.QLineEdit):
            if any(el in wgt.objectName() for el in not_necessary_wgs_names):
                pass
            else:
                required_to_fill_fields.append(wgt)
        elif isinstance(wgt, QtWidgets.QTreeWidget):
            required_to_fill_fields.append(wgt)
        elif isinstance(wgt, QtWidgets.QDateEdit):
            required_to_fill_fields.append(wgt)
    return required_to_fill_fields


class MainWindow(QtWidgets.QMainWindow, main_gui.Ui_MainWindow):
    """
    Класс-конструктор основного интерфейса приложения.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.setWindowTitle(f'{COPYRING_SIGN} ДЕМКА \"МОДУЛЬ УЧЁТА ОБОРУДОВАНИЯ\", для резюме - Шаповалов Р.В.')
        self.queue = queue.Queue()
        self.threads = []
        self.th_index_counter = 0
        self.th_index_write_counter = 0
        self.splash = QSplashScreen(QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}/clock_select_remain.png"))

        icon_add = QtGui.QIcon()
        icon_add.addPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon_delete = QtGui.QIcon()
        icon_delete.addPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        buttons_geometry = (28, 28, 28, 28)

        self.lineEdit_equipment_search.setPlaceholderText('поиск оборудования')
        self.pushButton_eq_add.setIcon(icon_add)
        self.pushButton_eq_delete.setIcon(icon_delete)
        self.pushButton_eq_add.setGeometry(*buttons_geometry)
        self.pushButton_eq_delete.setGeometry(*buttons_geometry)
        self.pushButton_eq_add.setToolTip("Добавить оборудование")
        self.pushButton_eq_delete.setToolTip("Удалить оборудование")

        self.comboBox_search_eq_type.addItems(EQUIPMENT_TYPE_LIST)

        self.tabWidget_equipment_info_table.setStyleSheet("QTabBar::tab {min-height: 40px;}")
        self.tabWidget_equipment_info_table.setTabText(self.tabWidget_equipment_info_table.indexOf(self.tab_general_information), "Общая\nинформация")
        self.tabWidget_equipment_info_table.setTabText(self.tabWidget_equipment_info_table.indexOf(self.tab_verification_info), "Сведения по поверке\n(калибровке), аттестации")
        self.tabWidget_equipment_info_table.setTabText(self.tabWidget_equipment_info_table.indexOf(self.tab_storage_info), "Сведения о хранении\n(консервации)")
        self.tabWidget_equipment_info_table.setTabText(self.tabWidget_equipment_info_table.indexOf(self.tab_repair_info), "Сведения о ремонте")

    def check_auth(self):
        '''
        Функция авторизации в приложении.
        Данная функция-заглушка оставлена для сохранения структуры демонстрационного приложения.
        '''
        return True

    def flashSplash(self):
        """
        Запуск приложения через заставку, условии успешной авторизации пользователя.
        """
        if self.check_auth():
            self.splash.show()
            self.asb = AppStatusBar(self)
            self.adbc = AllDbConnect()
            self.speq = StackedPageEquipment(self)
            self.window_show()

    def window_show(self):
        """
        Закрыть заставку и запустить основное окно
        :return:
        """
        self.show()
        self.splash.finish(self)

    def closeEvent(self, event) -> None:
        """
        Ф-я вызываемая при закрытии окна.
        """
        try:
            self.hide()
            if self.queue.full():
                for th_g, th_w in [getdata_thread.keys(), writedata_thread.keys()]:
                    if getdata_thread[th_g].isRunning():
                        getdata_thread[th_g].wait(5000)
                    if writedata_thread[th_w].isRunning():
                        writedata_thread[th_w].wait(5000)
            event.accept()
        except RuntimeError:
            pass
        except Exception as _err:
            err_msg = f"Строка {traceback.format_exc()} - Ошибка:\n{_err}"
            logging.error(err_msg)
        finally:
            event.accept()


class StackedPageEquipment(QtWidgets.QWidget):
    '''
    Класс обработки сигналов от страницы "ОБОРУДОВАНИЕ".
    '''
    def __init__(self, parent=None):
        super(StackedPageEquipment, self).__init__(parent)
        self.parent = parent

        self.queue = self.parent.queue
        self.th_index_counter = self.parent.th_index_counter
        self.th_index_write_counter = self.parent.th_index_write_counter

        self.parent.widget_equipment_info_left.hide()

        self.search_equipment()

        self.parent.comboBox_search_eq_type.currentTextChanged.connect(self.search_equipment)
        self.parent.listWidget_equipment_list.itemClicked['QListWidgetItem*'].connect(self.create_eq_filling_th)
        self.parent.listWidget_equipment_list.itemDoubleClicked['QListWidgetItem*'].connect(self.create_existing_equipment_window)
        self.parent.lineEdit_equipment_search.textChanged['QString'].connect(self.search_equipment)
        self.parent.pushButton_eq_add.clicked.connect(self.create_new_equipment_window)
        self.parent.pushButton_eq_delete.clicked.connect(self.delete_equipment)

    def check_visible(self):
        """
        Ф-я проверки видимости правой части и соотвественно
        скрыть или отобразить её.
        :return:
        """
        # isHidden()
        # isVisible()
        if self.parent.widget_equipment_info_left.isVisible():
            self.parent.widget_equipment_info_left.hide()

    def check_select_eq_list_el(self):
        """
        Ф-я проверки, что элемент из списка выбран
        :return: True | False
        """
        selected_list_elements = self.parent.listWidget_equipment_list.selectedItems()
        if selected_list_elements != []:
            self.parent.pushButton_eq_delete.setEnabled(True)
            return True
        else:
            self.parent.pushButton_eq_delete.setEnabled(False)
            return False

    def create_new_equipment_window(self):
        """
        Ф-я создания нового окна добавления оборудования.
        :return:
        """
        self.parent.window_new_eq = EquipmentInfoEdit(self.parent, Qt.Window)
        self.parent.window_new_eq.get_all_test_methods()
        self.parent.window_new_eq.form_show()

    def create_existing_equipment_window(self, current_list_item=None):
        """
        Ф-я создания нового окна для редактирования оборудования.
        :return:
        """
        current_sender = self.sender()
        current_equipment_listrow_data = None
        if self.check_select_eq_list_el():
            if current_sender.objectName() == "pushButton_eq_edit":
                current_equipment_listrow_data = self.listWidget_equipment_list.currentItem().text().split(", ")
            elif current_sender.objectName() == "listWidget_equipment_list":
                current_equipment_listrow_data = current_list_item.text().split(", ")
            self.window_existing_eq = ExistingEquipmentInfoEdit(self.parent, Qt.Window)
            current_equipment_inv_num = current_equipment_listrow_data[2]
            self.window_existing_eq.get_all_test_methods(current_equipment_inv_num)
        else:
            self.parent.asb.yellow_message(f"Сначала необходимо выбрать элемент из списка.")

    def create_eq_filling_th(self, current_equipment_list_row):
        """
        Ф-я создания потоков для заполнения вьюх с информацией об оборудовании.
        :param current_equipment_list_row:
        :return:
        """
        self.check_select_eq_list_el()
        current_equipment_listrow_data = current_equipment_list_row.text().split(", ")
        current_equipment_inv_num = current_equipment_listrow_data[2]
        searching_modes_arr = ["eq_general_information", "eq_verification_info", "eq_storage", "eq_repair"]
        for current_mode in searching_modes_arr:
            self.th_index_counter += 1
            getdata_thread[self.th_index_counter] = GetDataThreadNew(
                id=self.th_index_counter,
                queue=self.queue,
                current_func=self.parent.adbc.get_additional_tables_data,
                current_val=current_equipment_inv_num,
                currnt_mode=current_mode,
                parent=None
            )
            self.queue.put(getdata_thread[self.th_index_counter])
            getdata_thread[self.th_index_counter].task_done.connect(self.fill_eq_right_side_by_data, QtCore.Qt.QueuedConnection)
            getdata_thread[self.th_index_counter].finished.connect(self.parent.widget_equipment_info_left.show)
            getdata_thread[self.th_index_counter].start()

    def fill_eq_right_side_by_data(self, current_uploaded_data):
        """
        Ф-я заполнения вьюх с информацией об оборудовании.
        :param current_uploaded_data:
        :return:
        """
        current_df = current_uploaded_data[0]
        current_mode = current_uploaded_data[1]
        if current_mode == "eq_general_information":
            model = PandasTableModelVH(current_df)
            self.parent.tableView_general_information.setModel(model)
            self.parent.tableView_general_information.horizontalHeader().hide()
            self.parent.tableView_general_information.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.parent.tableView_general_information.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if current_mode == "eq_verification_info":
            model = PandasTableModelHH(current_df)
            self.parent.tableView_eq_verification_info.setModel(model)
            self.parent.tableView_eq_verification_info.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.parent.tableView_eq_verification_info.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.parent.tableView_eq_verification_info.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.parent.tableView_eq_verification_info.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.parent.tableView_eq_verification_info.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        if current_mode == "eq_storage":
            model = PandasTableModelHH(current_df)
            self.parent.tableView_storage_info.setModel(model)
            self.parent.tableView_storage_info.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.parent.tableView_storage_info.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.parent.tableView_storage_info.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        if current_mode == "eq_repair":
            model = PandasTableModelHH(current_df)
            self.parent.tableVieweq_repair_info.setModel(model)
            self.parent.tableVieweq_repair_info.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.parent.tableVieweq_repair_info.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def search_equipment(self, current_srch_val=None):
        """
        Функция запуска поиска оборудования и заполнения listWidget найденными совпадениями.
        """
        self.check_select_eq_list_el()
        current_sender = self.parent.sender()
        self.check_visible()
        self.parent.listWidget_equipment_list.clear()
        self.parent.listWidget_equipment_list.update()

        srch_val = None
        srch_mode = "всех посмотреть"
        called_func = self.fill_list_by_data

        if isinstance(current_sender, type(None)):
            pass
        else:
            current_sender_name = current_sender.objectName()
            if current_sender_name == "lineEdit_equipment_search":
                srch_val = current_srch_val
                srch_mode = self.parent.comboBox_search_eq_type.currentText()
                called_func = self.fill_list_by_data
            elif current_sender_name == "comboBox_search_eq_type":
                srch_val = self.parent.lineEdit_equipment_search.text()
                srch_mode = self.parent.comboBox_search_eq_type.currentText()
                called_func = self.fill_list_by_data

        self.th_index_counter += 1
        getdata_thread[self.th_index_counter] = GetDataThreadNew(
            id=self.th_index_counter,
            queue=self.queue,
            current_func=self.parent.adbc.get_equipment,
            current_val=srch_val,
            currnt_mode=srch_mode,
            parent=None
        )
        self.queue.put(getdata_thread[self.th_index_counter])
        getdata_thread[self.th_index_counter].task_done.connect(called_func, QtCore.Qt.QueuedConnection)
        getdata_thread[self.th_index_counter].start()

    def delete_equipment(self):
        """
        Удалить оборудование.
        :return:
        """
        current_equipment = self.parent.listWidget_equipment_list.currentItem().text()
        current_equipment = current_equipment.split(", ")
        current_equipment_name = current_equipment[0]
        current_equipment_inv_num = current_equipment[-1]

        mbox = MessageForm("Внимание!", "Да", "Нет", f"Вы уверены что хотите удалить оборудование: \"{current_equipment_name}\"?", self.parent)
        result = mbox.exec_()
        if result == QtWidgets.QDialog.Accepted:
            if current_equipment != '':
                self.parent.listWidget_equipment_list.clear()
                self.parent.listWidget_equipment_list.update()
                self.th_index_write_counter += 1
                writedata_thread[self.th_index_write_counter] = WriteDataThreadNew(
                    id=self.th_index_counter,
                    queue=self.queue,
                    current_func=self.parent.adbc.delete_equipment,
                    current_val=current_equipment_inv_num,
                    parent=None
                )
                self.queue.put(writedata_thread[self.th_index_write_counter])
                writedata_thread[self.th_index_write_counter].finished.connect(self.search_equipment)
                writedata_thread[self.th_index_write_counter].finished.connect(lambda: self.parent.asb.normal_message(f"Удалено оборудование: \"{current_equipment_name}\"."))
                writedata_thread[self.th_index_write_counter].start()
        elif result == QtWidgets.QDialog.Rejected:
            pass

    def fill_list_by_data(self, current_data=None):
        """
        Ф-я заполнения listWidget_equipment_list результатами поиска.
        Вызывается после завершения потока выгрузки данных.
        """
        if current_data != None and current_data != []:
            self.parent.listWidget_equipment_list.clear()
            self.parent.listWidget_equipment_list.update()
            for method_item_list in current_data:
                eq_data = [el if isinstance(el, str) else el.strftime("%d.%m.%Y") for el in method_item_list]
                itemTask = QtWidgets.QListWidgetItem(", ".join(eq_data))
                self.parent.listWidget_equipment_list.insertItem(0, itemTask)


class EquipmentInfoEdit(QtWidgets.QWidget, EQ_INFO_GUI.Ui_Form):
    '''
    Родительский класс интерфейса формы "Добавить/редактировать оборудование".
    '''

    current_equipment_inv_num = None
    current_equipment_name = None
    current_filling_status_list = None
    content_changed_control_val = 0

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)
        self.parent = parent
        self.queue = self.parent.queue
        self.th_index_counter = self.parent.th_index_counter
        self.th_index_write_counter = self.parent.th_index_write_counter

        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}hammer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(self.icon)

        icon_size_a, icon_size_b = 18, 18
        self.icon_add_passport = QtGui.QIcon()
        self.icon_add_passport.addPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}file_extension_pdf.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_eq_passport_add.setIcon(self.icon_add_passport)
        self.pushButton_eq_passport_add.setIconSize(QtCore.QSize(icon_size_a, icon_size_b))

        self.icon_upload_passport = QtGui.QIcon()
        self.icon_upload_passport.addPixmap(QtGui.QPixmap(f"{APP_SECRETS['TO_MEDIA_ICONS']}download.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_eq_passport_upload.setIcon(self.icon_upload_passport)
        self.pushButton_eq_passport_upload.setIconSize(QtCore.QSize(icon_size_a, icon_size_b))
        self.pushButton_eq_passport_upload.setToolTip("Скачать файл на компьютер")

        self.comboBox_eq_info_type.addItems(EQUIPMENT_TYPE_LIST[1:])


        self.clear_hint()

        self.fields_equipment_data = [
            self.lineEdit_eq_info_01_equipment_name,  # Наименование
            self.comboBox_eq_info_type,               # Тип
            self.lineEdit_eq_info_02_equipment_mark,  # Тип (марка) lineEdit_eq_info_02_equipment_mark
            self.lineEdit_eq_info_03_equipment_factory_num,  # Заводской номер
            self.lineEdit_eq_info_04_equipment_manufacturer,  # Завод изготовитель
            self.dateEdit_eq_info_05_eq_manufacturing_date,  # Дата изготовления
            self.dateEdit_eq_info_05_eq_commissioning_date,  # Дата ввода в эксплуатацию
            self.dateEdit_eq_regular_verification_date,  # Дата очередной поверки (аттестации)
            self.lineEdit_eq_info_06_equipment_inv_num,  # Инвентарный номер
            self.lineEdit_eq_info_07_eq_measuring_range_from,  # Диапазон тзмерений - ОТ
            self.lineEdit_eq_info_07_eq_measuring_range_to,  # Диапазон тзмерений - ДО
            self.lineEdit_eq_units_of_measurement,  # Ед.изм.
            self.lineEdit_eq_info_08_eq_accuracy_class,  # Класс точности (погрешность)
            self.lineEdit_eq_info_09_eq_technical_character,  # Основные тех. характеристики
            self.lineEdit_eq_info_10_eq_other_info,  # Иные сведения
            self.lineEdit_eq_passport_file,  # Паспорт (файл, полный путь)
            # Сведения о поверке (калибровке), аттестации
            self.lineEdit_eq_organization_verification,  # Организация проводившая поверку/аттестацию
            self.comboBox_eq_verification_result,  # Результат (пройдена/не пройдена)
            self.lineEdit_eq_verification_certificate,  # № свидетельства (сертификата), аттестата
            self.dateEdit_eq_verification_date,  # Дата проведения
            self.dateEdit_eq_regular_verification_date,  # Дата очередной поверки/аттестации
            # Сведения о хранении (консервации)
            self.lineEdit_eq_person_transferred_for_storage_not_necessary,  # Фамилия лица, переводившего СИ (ИО) на хранение (консервацию) - необязательное
            self.lineEdit_eq_person_transferred_from_storage_not_necessary,  # Фамилия, проводившего снятие СИ (ИО) с хранения (консервации) - необязательное
            self.dateEdit_eq_transfer_to_storage_date,  # Дата перевода на хранение (консервация)
            self.dateEdit_eq_removal_from_storage_date,  # Дата снятия с хранения (консервации)
            # Сведения о ремонте
            self.lineEdit_eq_org_repair_not_necessary,  # Лицо/организация проводившая ремонт - необязательное
            self.lineEdit_eq_description_result_not_necessary,  # Краткое описание работ и результат - необязательное
            self.dateEdit_eq_repair_date,  # Дата проведения
            # Метод испытаний
            self.treeWidget_eq_test_method,  # Метод испытаний
        ]
        self.required_to_fill_fields = initialisation_required_fields(self.fields_equipment_data)

        self.current_widgets_status = CheckEmptyFields(self.required_to_fill_fields)

        self.update_pasport_file_buttons_status()

        self.create_signals_for_widgets()
        self.pushButton_eq_passport_add.clicked.connect(self.get_eq_pasport_file_path)
        self.pushButton_eq_info_btn_cancel.clicked.connect(self.form_close)
        self.pushButton_eq_info_save.clicked.connect(self.save_equipment_data)

    def create_signals_for_widgets(self):
        """
        Ф-я создания сигналов, вызываемых при заполнении какого-либо из
        обязательных полей (QLineEdit, QTreeWidget) - перекрашивает поля.
        :return:
        """
        for wgt in self.required_to_fill_fields:
            if isinstance(wgt, QtWidgets.QLineEdit):
                wgt.textChanged.connect(self.repaint_fields)
            elif isinstance(wgt, QtWidgets.QTreeWidget):
                wgt.itemChanged.connect(self.repaint_fields)

    def update_pasport_file_buttons_status(self):
        """
        Ф-я обновления состояния и видимости кнопок добавления/выгрузки файла паспорта оборудования.
        Также обновляется состояние строки с именем/путь до файла
        :return:
        """
        self.lineEdit_eq_passport_file.setReadOnly(True)
        # Состояния кнопок по-умолчанию
        if self.lineEdit_eq_passport_file.text() == "":
            self.pushButton_eq_passport_upload.hide()
            self.pushButton_eq_passport_upload.setEnabled(False)
            self.pushButton_eq_passport_add.setToolTip("Добавить файл с паспортом оборудования")
        else:
            self.pushButton_eq_passport_upload.show()
            self.pushButton_eq_passport_upload.setEnabled(True)
            self.pushButton_eq_passport_add.setToolTip("Заменить файл с паспортом оборудования")

    def repaint_fields(self):
        """
        Вспомогательная ф-я перекрашивания полей.
        """
        self.clear_hint()
        self.current_filling_status_list = self.current_widgets_status.set_widget_colors()
        if self.current_filling_status_list == [] or any(item is False for item in self.current_filling_status_list):
            self.update_content_changed_control_val(1)
        else:
            self.update_content_changed_control_val(0)

    def update_content_changed_control_val(self, current_val=None):
        """
        Ф-я обновления переменной для контроля внесённых изменений
        """
        # 0 - Нет изменений
        # 1 - Изменения внесены
        self.content_changed_control_val = current_val

    def save_equipment_data(self):
        """
        Ф-я сохранения оборудования в БД.
        :return:
        """
        if self.current_filling_status_list is not None:
            if self.current_filling_status_list == [] or any(item is False for item in self.current_filling_status_list):
                self.content_changed_control_val = 1
                self.current_widgets_status.set_widget_colors()
                self.red_message("Необходимо заполнить обязательные поля!")
            else:
                to_write_data = get_value_from_fields(self.fields_equipment_data)
                current_date = dt.datetime.now()
                to_write_data.append("Иванов И.И.")
                to_write_data.append(current_date)

                self.th_index_write_counter += 1
                writedata_thread[self.th_index_write_counter] = WriteDataThreadNew(
                    id=self.th_index_counter,
                    queue=self.queue,
                    current_func=self.parent.adbc.insert_equipment_info,
                    current_val=to_write_data,
                    parent=None
                )
                self.queue.put(writedata_thread[self.th_index_write_counter])
                writedata_thread[self.th_index_write_counter].finished.connect(self.parent.speq.search_equipment)
                writedata_thread[self.th_index_write_counter].finished.connect(self.form_close)
                writedata_thread[self.th_index_write_counter].finished.connect(lambda: self.parent.asb.normal_message(f"Сохранёно оборудование \"{self.lineEdit_eq_info_01_equipment_name.text()}\""))
                writedata_thread[self.th_index_write_counter].start()
        else:
            self.red_message("Необходимо заполнить обязательные поля!")

    def get_all_test_methods(self, equipment_inv_num=None):
        """
        Ф-я выгрузки методов испытаний в потоке.
        :return:
        """
        current_sender = self.sender()
        self.th_index_counter += 1
        getdata_thread[self.th_index_counter] = GetDataThreadNew(
            id=self.th_index_counter,
            queue=self.queue,
            current_func=self.parent.adbc.get_test_method,
            current_val=None,
            currnt_mode="всех посмотреть",
            parent=None
        )
        self.queue.put(getdata_thread[self.th_index_counter])
        getdata_thread[self.th_index_counter].task_done.connect(self.get_all_test_methods_to_tree, QtCore.Qt.QueuedConnection)
        if current_sender.objectName() in ["listWidget_equipment_list", "pushButton_eq_edit"]:
            getdata_thread[self.th_index_counter].finished.connect(lambda: self.get_current_item_all_data(equipment_inv_num))
        getdata_thread[self.th_index_counter].start()

    def get_current_item_all_data(self, equipment_inv_num=None):
        """
        Ф-я выгрузки всех данных по конкретному оборудованию (выбранному и дабблкликед в списке).
        :param equipment_inv_num:
        :return:
        """
        if equipment_inv_num is not None:
            self.th_index_counter += 1
            getdata_thread[self.th_index_counter] = GetDataThreadNew(
                id=self.th_index_counter,
                queue=self.queue,
                current_func=self.parent.adbc.get_equipment,
                current_val=equipment_inv_num,
                currnt_mode="конкретный",
                parent=None
            )
            self.queue.put(getdata_thread[self.th_index_counter])
            getdata_thread[self.th_index_counter].task_done.connect(self.filling_fields, QtCore.Qt.QueuedConnection)
            getdata_thread[self.th_index_counter].start()

    def filling_fields(self, current_equipment_all_data):
        """
        Ф-я заполнения полей.
        """
        equipment_all_data_arr = current_equipment_all_data[0]
        self.current_equipment_name = equipment_all_data_arr[0]
        self.current_equipment_inv_num = equipment_all_data_arr[8]

        # Т.к. кол-во заполняемых виджетов совпадает с кол-ом выгруженных данных,
        # то count соответствуюет индексу элемента в equipment_all_data_arr
        for count, wgt in enumerate(self.fields_equipment_data):
            if isinstance(wgt, QtWidgets.QLineEdit):
                if wgt.objectName() == "lineEdit_eq_info_06_equipment_inv_num":
                    wgt.setReadOnly(True)
                if wgt.objectName() == "lineEdit_eq_passport_file":
                    file_name = self.passport_file_name
                    wgt.setText(file_name)
                wgt.setText(equipment_all_data_arr[count])
            elif isinstance(wgt, QtWidgets.QDateEdit):
                wgt.setDate(equipment_all_data_arr[count])
            elif isinstance(wgt, QtWidgets.QComboBox):
                wgt.setCurrentIndex(wgt.findText(equipment_all_data_arr[count], Qt.MatchExactly | Qt.MatchCaseSensitive))
            elif isinstance(wgt, QtWidgets.QTreeWidget):
                tree_wgt_items_list = equipment_all_data_arr[count].split(', ')
                if tree_wgt_items_list != []:
                    for itm_txt in tree_wgt_items_list:
                        for item in wgt.findItems(itm_txt, Qt.MatchContains | Qt.MatchRecursive):
                            item.setCheckState(0, Qt.Checked)
        self.update_pasport_file_buttons_status()
        self.form_show()

    def get_all_test_methods_to_tree(self, methods_data):
        """
        Ф-я заполнения дерева методов испытаний для дальнейшего выбора
        к сохраняемому/редактируемому оборудованию.
        :return:
        """
        columns_name = ["Название метода", "Нормативный документ"]
        self.treeWidget_eq_test_method.clear()
        self.treeWidget_eq_test_method.setColumnCount(len(columns_name))
        self.treeWidget_eq_test_method.setHeaderLabels(columns_name)
        test_methods_lst = []
        for n, test_method in enumerate(methods_data):
            item = QtWidgets.QTreeWidgetItem()
            item.setCheckState(0, Qt.Unchecked)  # item.setCheckState(0, Qt.Checked)
            item.setText(0, test_method[0])
            item.setText(1, test_method[1])
            test_methods_lst.append(item)
        self.treeWidget_eq_test_method.addTopLevelItems(test_methods_lst)
        for col, val in enumerate(columns_name):
            self.treeWidget_eq_test_method.resizeColumnToContents(col)
        self.treeWidget_eq_test_method.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.treeWidget_eq_test_method.update()

    def get_eq_pasport_file_path(self):
        """
        Функция получения пути до исполняемого файла DW.
        """
        file = QtWidgets.QFileDialog.getOpenFileName(
            parent=None,
            caption="Выбрать файл",
            directory=r"C:\\",
            filter="All (*);;Exes (*.pdf *.doc *.docx)",
            initialFilter="Exes (*.pdf *.doc *.docx)")
        if file[0]:
            self.lineEdit_eq_passport_file.setText(str(file[0]))

    def normal_message(self, cur_text):
        """
        Обычное сообщение.
        """
        self.label_extended_hint.setStyleSheet("background-color : rgb(239, 240, 241); font: bold 14px 'Arial'; color: black;")
        self.label_extended_hint.setText(f'{cur_text}')
        self.frame_extended_hint.show()

    def green_message(self, cur_text):
        """
        Зеленое сообщение.
        """
        self.label_extended_hint.setStyleSheet("background-color : green; font: bold 14px 'Arial'; color: black;")
        self.label_extended_hint.setText(f'{cur_text}')
        self.frame_extended_hint.show()

    def red_message(self, cur_text=None):
        """
        Красное сообщение.
        """
        self.label_extended_hint.setStyleSheet("background-color : red; font: bold 14px 'Arial'; color: white;")
        self.label_extended_hint.setText(f'{cur_text}')
        self.frame_extended_hint.show()

    def clear_hint(self):
        """
        Очистка строки от предыдущего сообщения.
        """
        self.label_extended_hint.setStyleSheet("background-color : rgb(239, 240, 241); font: bold 14px 'Arial'; color: black;")
        self.label_extended_hint.clear()
        self.frame_extended_hint.hide()

    def form_show(self):
        """
        Функция вызова отображения формы.
        """
        current_sender = self.sender()
        if current_sender is not None:
            if current_sender.objectName() == "pushButton_eq_add":
                self.setWindowTitle('Добавить оборудование')
            else:
                self.setWindowTitle(f'Редактировать информацию об оборудовании: \"{self.current_equipment_name}\" - Инв.№ {self.current_equipment_inv_num}')
        self.showNormal()

    def form_close(self):
        """
        Переопределенная ф-я закрытия формы.
        """
        self.close()

    def closeEvent(self, event):
        """
        Ф-я вызываемая при закрытии формы.
        :param event:
        :return:
        """
        if self.content_changed_control_val == 1:
            mbox = MessageForm("Внимание!", "Закрыть без сохранения", "Отмена", "Вы внесли изменения, но не сохранили их.", self)
            result = mbox.exec_()
            if result == QtWidgets.QDialog.Accepted:
                event.accept()
            elif result == QtWidgets.QDialog.Rejected:
                self.save_equipment_data()
                event.ignore()
            else:
                event.ignore()
        else:
            event.accept()


class ExistingEquipmentInfoEdit(EquipmentInfoEdit):
    '''
    Класс интерфейса формы "Добавить/редактировать оборудование"
    '''

    current_equipment_inv_num = None
    current_equipment_name = None

    def __init__(self, parent=None, flags=None):
        super().__init__(parent, flags)
        self.passport_file_name = None
        self.pushButton_eq_passport_upload.clicked.connect(self.upload_pasport_file)

    def get_eq_pasport_file_path(self):
        """
        Функция получения пути до файла.
        """
        file = QtWidgets.QFileDialog.getOpenFileName(
            parent=None,
            caption="Выбрать файл",
            directory=r"C:\\",
            filter="All (*);;Exes (*.pdf *.doc *.docx)",
            initialFilter="Exes (*.pdf *.doc *.docx)")
        if file[0]:
            self.lineEdit_eq_passport_file.setText(str(file[0]))

    def upload_pasport_file(self):
        """
        Ф-я выгрузки файла из БД.
        В ДАННОЙ ДЕМКЕ ОТСУТСТВУЕТ ФУНКЦИОНАЛ ВЗИМОДЕЙСТВИЯ С FASTAPI
        """
        pass

    def clear_all_fields(self):
        """
        Ф-я очистки полей.
        Берутся все объекты-виджеты из соответствующего массива виджетов.
        """
        for wgt in self.fields_equipment_data:
            if isinstance(wgt, QtWidgets.QLineEdit) or isinstance(wgt, QtWidgets.QDateEdit):
                wgt.clear()



# точка входа:
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ce_window = MainWindow()
    ce_window.flashSplash()
    sys.exit(app.exec_())