# -*- coding: utf-8 -*-
# ce_variables.py

import os
import locale
import platform
import tempfile
from pathlib import Path
import logging
import socket
import uuid

"""
Различные переменные для приложения.
"""

# ДЛЯ ПРИМЕРА ЗНАЧЕНИЯ УКАЗАНЫ В СЛОВАРЕ, В РЕАЛЬНОМ ПРИЛОЖЕНИИ ВСЕ "СЕКРЕТНЫЕ" ЗНАЧЕНИЯ ХРАНЯТСЯ В .env.
# ТАКЖЕ В РЕАЛЬНОМ ПРИЛОЖЕНИИ ИСПОЛЬЗУЕТСЯ СОЕДИНЕНИЕ С СУБД PSQL ЧЕРЕЗ SSH-ТОННЕЛЬ, А В ДАННОМ ПРИМЕРЕ ИСПОЛЬЗУЕТСЯ ЛОКАЛЬНАЯ БД В DOCKER.

#from dotenv import dotenv_values
# Выгрузка "секретов" из .env
#config_env = dotenv_values(".env")

COPYRING_SIGN = u"\U000000A9"

# Преобразование выгруженных значений в словарь:
APP_SECRETS = {
    'APP_AUTOR_FULL_NAME': 'R.V.Shapovalov',
    'APP_ORGANIZATION_NAME': 'R.V.Shapovalov',
    'APP_ORGANIZATION_DOMAIN': 'example.ru',
    'APP_AUTOR_EMAIL': 'example@example.ru',
    'APP_NAME': 'example_DMS_OBP',
    'SRV_LOCAL_PSQL_PORT': '54321',
    'PSQL_DB_NAME': 'example_db',
    'PSQL_DB_USER': 'db_user',
    'PSQL_DB_PASS': 'db_password',
    'PSQL_DB_HOST': 'localhost',
    'TO_MEDIA_ICONS': './media/icons/icons_3000/32x32/',
}

# Инициализация словаря и и списка для комбобоксов с типом лабораторного оборудования
EQUIPMENT_TYPE_D = {
    "all": "Все типы оборудования",
    "general": "Общелабораторное",
    "measuring": "Измерительное",
    "specialized": "Специализированное",
    "experimental": "Испытательное",
    "analytical": "Аналитическое"
}
EQUIPMENT_TYPE_LIST = [i for i in EQUIPMENT_TYPE_D.values()]

# Инициализация MAC-адреса данного ПК
CURRENT_PC_MAC = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])

def create_necessary_directories(current_programdata):
    """
    Создание необходимых директорий и файлов.
    :param current_programdata:
    :return:
    """
    # Создание директории example_app (для хранения настроек, и т.п.), если её нет
    Path(f'{current_programdata}/example_app').mkdir(parents=True, exist_ok=True)
    # Создание католога для временных-файлов
    Path(f'{current_programdata}/example_app/tmp').mkdir(parents=True, exist_ok=True)
    # Создание католога для лог-файлов
    Path(f'{current_programdata}/example_app/logs').mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=f'{current_programdata}/example_app/logs/' + f"{str(socket.gethostname())}_example_app.log",
        filemode='a+',
        format='%(asctime)s, %(levelname)s: %(message)s',
        datefmt='%d.%m.%Y, %H:%M:%S',
        level=logging.INFO
    )

if platform.system() == 'Windows':
    locale.setlocale(locale.LC_ALL, 'ru')
    current_user_profile = os.environ['USERPROFILE']
    current_temp_dir = tempfile.gettempdir()
    current_programdata = os.getenv('ProgramData')
    create_necessary_directories(current_programdata)

elif platform.system() == 'Linux':
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')
    current_user_profile = os.path.expanduser('~')
    current_temp_dir = tempfile.gettempdir()
    current_programdata = current_user_profile
    create_necessary_directories(current_programdata)

# Список частей имен виджетов не обязательных к заполнению
not_necessary_wgs_names = ["_file", "_not_necessary"]