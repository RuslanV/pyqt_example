# -*- coding: utf-8 -*-
# sql_orm_conn.py

from sqlalchemy import create_engine, text, Index, MetaData, select, insert, update, delete, Table, Column, String, Integer, Unicode, UnicodeText, Text, DateTime, Date, Boolean, Float, VARBINARY, NCHAR, BINARY, func, distinct, asc, desc, or_, and_, extract, ForeignKey, ForeignKeyConstraint, Identity, event, DDL
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
import pandas as pd
from constants.ce_variables import *

"""
Модуль для взаимодействия с БД.
"""

Base = declarative_base()


class ParentEqTable(Base):
    """
    Класс-описание таблицы - ОБОРУДОВАНИЕ.
    """
    __tablename__ = "table_equipment"
    equipment_name = Column(String)                                         # Наименование
    equipment_type = Column(String)                                         # Тип
    equipment_mark = Column(String)                                         # Тип (марка)
    equipment_factory_num = Column(String)                                  # Заводской номер , primary_key=True, nullable=False
    equipment_manufacturer = Column(String)                                 # Завод-изготовитель
    eq_manufacturing_date = Column(Date)                                    # Дата изготовления
    eq_commissioning_date = Column(Date)                                    # Дата ввода в эксплуатацию
    eq_next_verification = Column(Date)                                     # Дата очередной поверки (аттестации)
    equipment_inv_num = Column(String, primary_key=True)                    # Инвентарный номер
    eq_measuring_range_from = Column(String)                                # Диапазон тзмерений - ОТ
    eq_measuring_range_to = Column(String)                                  # Диапазон тзмерений - ДО
    eq_units_of_measurement = Column(String)                                # Ед.изм.
    eq_accuracy_class = Column(String)                                      # Класс точности (погрешность)
    eq_technical_character = Column(String)                                 # Основные тех. характеристики
    eq_other_info = Column(String)                                          # Иные сведения
    eq_passport_file_name = Column(String, default=None)                    # Паспорт имя файла
    eq_passport_file = Column(BYTEA, default=None)                         # Паспорт
    # Сведения о поверке (калибровке), аттестации
    eq_organization_verification = Column(String)                           # Организация проводившая поверку/аттестацию
    eq_verification_result = Column(String)                                 # Результат (пройдена/не пройдена)
    eq_verification_certificate = Column(String)                            # № свидетельства (сертификата), аттестата
    eq_verification_date = Column(Date)                                     # Дата проведения
    eq_regular_verification_date = Column(Date)                             # Дата очередной поверки/аттестации
    # Сведения о хранении (консервации)
    eq_person_transferred_for_storage = Column(String)                      # Фамилия лица, переводившего СИ (ИО) на хранение (консервацию)
    eq_person_transferred_from_storage = Column(String)                     # Фамилия, проводившего снятие СИ (ИО) с хранения (консервации)
    eq_transfer_to_storage_date = Column(Date)                              # Дата перевода на хранение (консервация)
    eq_removal_from_storage_date = Column(Date)                             # Дата снятия с хранения (консервации)
    # Сведения о ремонте
    eq_org_repair = Column(String)                                          # Лицо/организация проводившая ремонт
    eq_description_result = Column(String)                                  # Краткое описание работ и результат
    eq_repair_date = Column(Date)                                           # Дата проведения
    # Метод испытаний
    eq_test_method = Column(String)                                         # Метод испытаний
    # Пользователь добавивший запись
    eq_added_user = Column(String)                                          # Пользователь добавивший запись
    # Дата добавления оборудования
    eq_date_added = Column(Date)                                            # Дата добавления записи
    children_eq_info = relationship(
        "ChildEqTableInfo",
        back_populates="parent",
        cascade="all, delete",
        passive_deletes=True,
    )
    children_eq_storage = relationship(
        "ChildEqTableStorage",
        back_populates="parent",
        cascade="all, delete",
        passive_deletes=True,
    )
    children_eq_repair = relationship(
        "ChildEqTableStorage",
        back_populates="parent",
        cascade="all, delete",
        passive_deletes=True,
    )


class ChildEqTableInfo(Base):
    """
    Класс-описание таблицы - ОБОРУДОВАНИЕ - информация о поверке(калибровке), аттестации.
    """
    __tablename__ = "table_eq_verification_info"
    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, default=1)                        # Первичный ключ
    equipment_factory_num = Column(String)                                                                   # Заводской номер
    equipment_inv_num = Column(String, ForeignKey("table_equipment.equipment_inv_num", ondelete="CASCADE"))  # Инвентарный номер
    eq_organization_verification = Column(String)                                                            # Организация проводившая поверку/аттестацию
    eq_verification_result = Column(String)                                                                  # Результат (пройдена/не пройдена)
    eq_verification_certificate = Column(String)                                                             # № свидетельства (сертификата), аттестата
    eq_verification_date = Column(Date)                                                                      # Дата проведения
    eq_regular_verification_date = Column(Date)                                                              # Дата очередной поверки/аттестации
    eq_added_user = Column(String)                                                                           # Пользователь добавивший запись
    eq_date_added = Column(Date)                                                                             # Дата добавления записи
    idx_eqvi = Index('equipment_inv_num', 'eq_verification_date', unique=True)                               # Составной индекс
    parent = relationship("ParentEqTable", back_populates="children_eq_info")                                # Связь с родительской таблицей


class ChildEqTableStorage(Base):
    """
    Класс-описание таблицы - ОБОРУДОВАНИЕ - информация о хранении/консервации.
    """
    __tablename__ = "table_eq_storage"
    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, default=1)                                        # Первичный ключ
    equipment_factory_num = Column(String)                                                                                   # Заводской номер
    equipment_inv_num = Column(String, ForeignKey("table_equipment.equipment_inv_num", ondelete="CASCADE"))                  # Инвентарный номер
    eq_person_transferred_for_storage = Column(String)                                                                       # Фамилия лица, переводившего СИ (ИО) на хранение (консервацию)
    eq_person_transferred_from_storage = Column(String)                                                                      # Фамилия, проводившего снятие СИ (ИО) с хранения (консервации)
    eq_transfer_to_storage_date = Column(Date)                                                                               # Дата перевода на хранение (консервация)
    eq_removal_from_storage_date = Column(Date)                                                                              # Дата снятия с хранения (консервации)
    eq_added_user = Column(String)                                                                                           # Пользователь добавивший запись
    eq_date_added = Column(Date)                                                                                             # Дата добавления записи
    idx_eqsi = Index('equipment_inv_num', 'eq_transfer_to_storage_date', 'eq_person_transferred_from_storage', unique=True)  # Составной индекс
    parent = relationship("ParentEqTable", back_populates="children_eq_storage")                                             # Связь с родительской таблицей


class ParentTestsMethods(Base):
    """
    Класс-описание таблицы - МЕТОДЫ ИСПЫТАНИЙ.
    """
    __tablename__ = "table_test_methods"
    method_name = Column(String, primary_key=True)
    method_normative_document = Column(String, primary_key=True)
    method_test_object_name = Column(String, primary_key=True)
    method_definable_characteristic = Column(String)
    method_note = Column(String)


class ChildEqTableRepair(Base):
    """
    Класс-описание таблицы - ОБОРУДОВАНИЕ - информация о ремонте.
    """
    __tablename__ = "table_eq_repair"
    id = Column(Integer, Identity(start=1, cycle=False), primary_key=True, default=1)                        # Первичный ключ
    equipment_factory_num = Column(String)                                                                   # Заводской номер
    equipment_inv_num = Column(String, ForeignKey("table_equipment.equipment_inv_num", ondelete="CASCADE"))  # Инвентарный номер
    eq_org_repair = Column(String)                                                                           # Лицо/организация проводившая ремонт
    eq_description_result = Column(String)                                                                   # Краткое описание работ и результат
    eq_repair_date = Column(Date)                                                                            # Дата проведения
    eq_added_user = Column(String)                                                                           # Пользователь добавивший запись
    eq_date_added = Column(Date)                                                                             # Дата добавления записи
    idx_eqri = Index('equipment_inv_num', 'eq_repair_date', unique=True)                                     # Составной индекс
    parent = relationship("ParentEqTable", back_populates="children_eq_repair")                              # Связь с родительской таблицей


class AllDbConnect:
    """
    Класс для взимодействия со всеми БД и СУБД.
    Используется в новой CE - Системе документооборота.
    """
    def __init__(self):
        self.table_equipment = ParentEqTable.__table__
        self.table_eq_verification_info_table = ChildEqTableInfo.__table__
        self.table_eq_storage_info_table = ChildEqTableStorage.__table__
        self.table_eq_repair_info_table = ChildEqTableRepair.__table__
        self.table_test_methods = ParentTestsMethods.__table__
        self.metadata = MetaData()
        DATABASE_URL = f'postgresql://{APP_SECRETS["PSQL_DB_USER"]}:{APP_SECRETS["PSQL_DB_PASS"]}@{APP_SECRETS["PSQL_DB_HOST"]}:{APP_SECRETS["SRV_LOCAL_PSQL_PORT"]}/{APP_SECRETS["PSQL_DB_NAME"]}'
        self.engine_psql = create_engine(DATABASE_URL, echo=False, pool_recycle=3600, pool_pre_ping=True, client_encoding="utf8")
        Base.metadata.create_all(self.engine_psql)
        self.create_views()

    def create_views(self):
        """
        Ф-я создания вьюх/триггеров для различных....
        :return:
        """
        stmt_list = []
        # Создание триггеров для автозаполнения таблиц с информацией об оборудовании
        stmt_create_triggers = """
        -- Создать триггерную функцию для заполнения таблицы - информация о хранении/консервации
        CREATE OR REPLACE FUNCTION after_table_equipment_insert_storage() 
        RETURNS trigger AS
        $$
          BEGIN
          INSERT INTO table_eq_storage(equipment_factory_num, equipment_inv_num, eq_person_transferred_for_storage, eq_person_transferred_from_storage, eq_transfer_to_storage_date, eq_removal_from_storage_date, eq_added_user, eq_date_added) 
          VALUES(NEW.equipment_factory_num, NEW.equipment_inv_num, NEW.eq_person_transferred_for_storage, NEW.eq_person_transferred_from_storage, NEW.eq_transfer_to_storage_date, NEW.eq_removal_from_storage_date, NEW.eq_added_user, NEW.eq_date_added);
          RETURN NEW;
          END;
        $$
        LANGUAGE 'plpgsql';

        -- Создать триггерную функцию для заполнения таблицы - информация о ремонте
        CREATE OR REPLACE FUNCTION after_table_equipment_insert_repair() 
        RETURNS trigger AS
        $$
          BEGIN
          INSERT INTO table_eq_repair(equipment_factory_num, equipment_inv_num, eq_org_repair, eq_description_result, eq_repair_date, eq_added_user, eq_date_added) 
          VALUES(NEW.equipment_factory_num, NEW.equipment_inv_num, NEW.eq_org_repair, NEW.eq_description_result, NEW.eq_repair_date, NEW.eq_added_user, NEW.eq_date_added);
          RETURN NEW;
          END;
        $$
        LANGUAGE 'plpgsql';

        -- Создать триггерную функцию для заполнения таблицы - информация о поверке(калибровке), аттестации
        CREATE OR REPLACE FUNCTION after_table_equipment_insert_verification_info() 
        RETURNS trigger AS
        $$
          BEGIN
          INSERT INTO table_eq_verification_info(equipment_factory_num, equipment_inv_num, eq_organization_verification, eq_verification_result, eq_verification_certificate, eq_verification_date, eq_regular_verification_date, eq_added_user, eq_date_added) 
          VALUES(NEW.equipment_factory_num, NEW.equipment_inv_num, NEW.eq_organization_verification, NEW.eq_verification_result, NEW.eq_verification_certificate, NEW.eq_verification_date, NEW.eq_regular_verification_date, NEW.eq_added_user, NEW.eq_date_added);
          RETURN NEW;
          END;
        $$
        LANGUAGE 'plpgsql';

        -- Удалить триггеры, если есть
        DROP TRIGGER IF EXISTS eq_aft_insert_storage on public.table_equipment;
        DROP TRIGGER IF EXISTS eq_aft_insert_repair on public.table_equipment;
        DROP TRIGGER IF EXISTS eq_aft_insert_verification_info on public.table_equipment;

        -- Создать триггеры заново
        CREATE TRIGGER eq_aft_insert_storage 
        AFTER INSERT ON table_equipment FOR EACH ROW 
        EXECUTE PROCEDURE after_table_equipment_insert_storage();

        CREATE TRIGGER eq_aft_insert_repair 
        AFTER INSERT ON table_equipment FOR EACH ROW 
        EXECUTE PROCEDURE after_table_equipment_insert_repair();

        CREATE TRIGGER eq_aft_insert_verification_info 
        AFTER INSERT ON table_equipment FOR EACH ROW 
        EXECUTE PROCEDURE after_table_equipment_insert_verification_info();
        
        -- ДЛЯ ПРИМЕРА ЗАПОЛНИТЬ ТАБЛИЦУ С МЕТОДАМИ ИСПЫТАНИЙ, Т.К. В ДЕМКЕ НЕТ МОДУЛЯ "МЕТОДЫ ИСПЫТАНИЙ"
        """
        stmt_list.append(stmt_create_triggers)

        stmt_add_example_method = """
        insert into table_test_methods (method_name, method_normative_document, method_test_object_name, method_definable_characteristic, method_note) values ('Огнестойкость', 'ГОСТ-123', 'Плита перекрытия', 'минуты', 'Для демки') On CONFLICT (method_name, method_normative_document, method_test_object_name) DO NOTHING;;
        """
        stmt_list.append(stmt_add_example_method)

        for key in EQUIPMENT_TYPE_D.keys():
            if key == "all":
                stmt_list.append(
                    "CREATE OR REPLACE VIEW all_eq_view AS SELECT equipment_name, equipment_mark, equipment_inv_num FROM table_equipment ORDER BY equipment_name DESC;")
            else:
                stmt_list.append(
                    f"CREATE OR REPLACE VIEW {key}_eq_view AS SELECT equipment_name, equipment_mark, equipment_inv_num FROM table_equipment WHERE equipment_type = '{EQUIPMENT_TYPE_D[key]}' ORDER BY equipment_name DESC;")
        with self.engine_psql.begin() as connection:
            for stmt in stmt_list:
                connection.execute(text(stmt))

    def insert_equipment_info(self, current_data_list=None):
        '''
        Добавить запись об оборудовании.
        '''
        columns_keys = [key.name for key in inspect(self.table_equipment).columns]
        record_dict = dict(zip(columns_keys, current_data_list))
        if record_dict["eq_passport_file_name"] == None:
            record_dict.pop("eq_passport_file_name")
            record_dict.pop("eq_passport_file")
        else:
            pass
        stmt_all_info = insert(self.table_equipment). \
            values(current_data_list). \
            on_conflict_do_update(index_elements=['equipment_inv_num'], set_=record_dict)
        with self.engine_psql.begin() as connection:
            connection.execute(stmt_all_info)

    def get_equipment(self, srch_text=None, search_mode=None):
        """
        Поиск оборудовании в БД.
        в зависимости от признака/режима поиска (search_mode):
        search_mode == 'ищет' - Поиск похожих;
        search_mode == 'всех посмотреть' - выгрузка всех записей.
        """
        stmt = None
        if search_mode in EQUIPMENT_TYPE_LIST:
            for key in EQUIPMENT_TYPE_D.keys():
                if EQUIPMENT_TYPE_D[key] == search_mode:
                    if srch_text is not None and srch_text != "":
                        stmt = select(
                            self.table_equipment.c.equipment_name,
                            self.table_equipment.c.equipment_mark,
                            self.table_equipment.c.equipment_inv_num
                        ).filter(
                            or_(
                                self.table_equipment.c.equipment_name.ilike(f"%{srch_text}%"),
                                self.table_equipment.c.equipment_inv_num.contains(srch_text),
                            )
                        )
                    else:
                        if search_mode != "Все типы оборудования":
                            stmt = select(
                                self.table_equipment.c.equipment_name,
                                self.table_equipment.c.equipment_mark,
                                self.table_equipment.c.equipment_inv_num
                            ).filter(
                                self.table_equipment.c.equipment_type == search_mode
                            )
                        else:
                            stmt = select(
                                self.table_equipment.c.equipment_name,
                                self.table_equipment.c.equipment_mark,
                                self.table_equipment.c.equipment_inv_num
                            )

        elif search_mode == 'всех посмотреть':
            stmt = select(
                self.table_equipment.c.equipment_name,
                self.table_equipment.c.equipment_mark,
                self.table_equipment.c.equipment_inv_num
            )

        elif search_mode == 'конкретный':
            stmt = select(
                self.table_equipment.c.equipment_name,
                self.table_equipment.c.equipment_type,
                self.table_equipment.c.equipment_mark,
                self.table_equipment.c.equipment_factory_num,
                self.table_equipment.c.equipment_manufacturer,
                self.table_equipment.c.eq_manufacturing_date,
                self.table_equipment.c.eq_commissioning_date,
                self.table_equipment.c.eq_next_verification,
                self.table_equipment.c.equipment_inv_num,
                self.table_equipment.c.eq_measuring_range_from,
                self.table_equipment.c.eq_measuring_range_to,
                self.table_equipment.c.eq_units_of_measurement,
                self.table_equipment.c.eq_accuracy_class,
                self.table_equipment.c.eq_technical_character,
                self.table_equipment.c.eq_other_info,
                self.table_equipment.c.eq_passport_file_name,
                self.table_equipment.c.eq_organization_verification,
                self.table_equipment.c.eq_verification_result,
                self.table_equipment.c.eq_verification_certificate,
                self.table_equipment.c.eq_verification_date,
                self.table_equipment.c.eq_regular_verification_date,
                self.table_equipment.c.eq_person_transferred_for_storage,
                self.table_equipment.c.eq_person_transferred_from_storage,
                self.table_equipment.c.eq_transfer_to_storage_date,
                self.table_equipment.c.eq_removal_from_storage_date,
                self.table_equipment.c.eq_org_repair,
                self.table_equipment.c.eq_description_result,
                self.table_equipment.c.eq_repair_date,
                self.table_equipment.c.eq_test_method,
            ).filter(self.table_equipment.c.equipment_inv_num == srch_text)

        if stmt is not None:
            with self.engine_psql.connect() as connection:
                uploaded_data = connection.execute(stmt).fetchall()
                uploaded_data = list(uploaded_data)
                return uploaded_data

    def delete_equipment(self, current_equipment_inv_num):
        """
        Удалить оборудование из БД.
        :param current_equipment_inv_num:
        :return:
        """
        stmt = (delete(self.table_equipment).where(self.table_equipment.c.equipment_inv_num == current_equipment_inv_num))
        with self.engine_psql.begin() as connection:
            connection.execute(stmt)

    def get_additional_tables_data(self, srch_text=None, search_mode=None):
        """
        Ф-я выгрузки данных из вьюх с информацией об оборудовании.
        :param srch_text:
        :param search_mode:
        :return:
        """
        if search_mode == "eq_general_information":
            stmt = select(
                self.table_equipment.c.equipment_name.label("Наименование"),
                self.table_equipment.c.equipment_type.label("Тип"),
                self.table_equipment.c.equipment_mark.label("Тип (марка)"),
                self.table_equipment.c.equipment_factory_num.label("Заводской номер"),
                self.table_equipment.c.equipment_manufacturer.label("Завод-изготовитель"),
                self.table_equipment.c.eq_manufacturing_date.label("Дата изготовления"),
                self.table_equipment.c.eq_commissioning_date.label("Дата ввода в эксплуатацию"),
                self.table_equipment.c.eq_next_verification.label("Дата очередной поверки (аттестации)"),
                self.table_equipment.c.equipment_inv_num.label("Инвентарный номер"),
                self.table_equipment.c.eq_measuring_range_from.label("Диапазон измерений - ОТ"),
                self.table_equipment.c.eq_measuring_range_to.label("Диапазон измерений - ДО"),
                self.table_equipment.c.eq_units_of_measurement.label("Ед.изм."),
                self.table_equipment.c.eq_accuracy_class.label("Класс точности (погрешность)"),
                self.table_equipment.c.eq_technical_character.label("Основные тех. характеристики"),
                self.table_equipment.c.eq_other_info.label("Иные сведения")
            ).filter(self.table_equipment.c.equipment_inv_num == srch_text)
        elif search_mode == "eq_verification_info":
            stmt = select(
                self.table_eq_verification_info_table.c.eq_organization_verification.label("Организация проводившая\nповерку/аттестацию"),
                self.table_eq_verification_info_table.c.eq_verification_date.label("Дата проведения"),
                self.table_eq_verification_info_table.c.eq_regular_verification_date.label("Дата очередной\nповерки/аттестации"),
                self.table_eq_verification_info_table.c.eq_verification_result.label("Результат\n(пройдена/не пройдена)"),
                self.table_eq_verification_info_table.c.eq_verification_certificate.label("№ свидетельства\n(сертификата/аттестата)")
            ).filter(self.table_eq_verification_info_table.c.equipment_inv_num == srch_text)
        elif search_mode == "eq_storage":
            stmt = select(
                self.table_eq_storage_info_table.c.eq_transfer_to_storage_date.label("Дата перевода\nна хранение\n(консервация)"),
                self.table_eq_storage_info_table.c.eq_person_transferred_for_storage.label("Фамилия лица,\nпереводившего СИ(ИО)\nна хранение (консервацию)"),
                self.table_eq_storage_info_table.c.eq_removal_from_storage_date.label("Дата снятия\nс хранения\n(консервации)"),
                self.table_eq_storage_info_table.c.eq_person_transferred_from_storage.label("Фамилия лица,\nпроводившего\nснятие СИ (ИО)\nс хранения (консервации)"),
            ).filter(self.table_eq_storage_info_table.c.equipment_inv_num == srch_text)
        elif search_mode == "eq_repair":
            stmt = select(
                self.table_eq_repair_info_table.c.eq_org_repair.label("Лицо/организация\nпроводившая ремонт"),
                self.table_eq_repair_info_table.c.eq_repair_date.label("Дата проведения"),
                self.table_eq_repair_info_table.c.eq_description_result.label("Краткое описание\nработ и результат"),
            ).filter(self.table_eq_repair_info_table.c.equipment_inv_num == srch_text)

        with self.engine_psql.connect() as connection:
            uploaded_data = connection.execute(stmt).all()
            df = pd.DataFrame(uploaded_data)
            return df, search_mode

    def get_test_method(self, srch_text=None, search_mode=None):
        '''
        Поиск метода испытания в БД.
        в зависимости от признака/режима поиска (search_mode):
        search_mode == 'ищет' - Поиск похожих;
        search_mode == 'выбрал' - Поиск конкретной записи;
        search_mode == 'всех посмотреть' - выгрузка всех записей.
        '''
        stmt = None
        if search_mode == 'ищет':
            stmt = select(self.table_test_methods).filter \
                    (
                    or_(
                        self.table_test_methods.c.method_name.ilike(f"%{srch_text}%"),
                        self.table_test_methods.c.method_normative_document.ilike(f"%{srch_text}%"),
                        self.table_test_methods.c.method_test_object_name.ilike(f"%{srch_text}%")
                    )
                )
        elif search_mode == 'конкретный':
            stmt = select(self.table_test_methods). \
                filter(
                and_(
                    self.table_test_methods.c.method_name == srch_text[0],
                    self.table_test_methods.c.method_normative_document == srch_text[1],
                    self.table_test_methods.c.method_test_object_name == srch_text[2]
                )
            )
        elif search_mode == 'всех посмотреть':
            stmt = select(self.table_test_methods)

        elif search_mode == 'названия объектов':
            stmt = f"SELECT * FROM tm_ob_names_tm_view;"

        if stmt is not None:
            if isinstance(stmt, str):
                with self.engine_psql.connect() as connection:
                    # Выполнить транзакцию:
                    uploaded_data = connection.execute(text(stmt)).fetchall()
                    return uploaded_data
            else:
                with self.engine_psql.connect() as connection:
                    # Выполнить транзакцию:
                    uploaded_data = connection.execute(stmt).fetchall()
                    uploaded_data = list(uploaded_data)
                    return uploaded_data