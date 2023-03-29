# pyqt_example
Пример кода кроссплатформенного desktop-приложения (стек: Python 3.8+, QT5+, PSQL, SQLalchemy)
- ООП
- многопоточность (включая переопределение базового класса, очередь)
- концепция модель-представление
- ORM
- генераторы
- различные типы данных
- и т.п.

## Для работы приложения необходима БД, которую можно запустить в docker.

Содержание Dockerfile:
```
FROM postgres:latest
RUN apt-get update && apt-get install -y locales
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8
```
Сборка контейнера:
```
docker run -d --name example_app_pgdb -e POSTGRES_PASSWORD=db_password -e POSTGRES_USER=db_user -e POSTGRES_DB=example_db -p 54321:5432 example_app_pgdb
```
