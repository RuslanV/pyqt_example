## pyqt_example
Пример кода кроссплатформенного (Windows/Linux) desktop-приложения (стек: Python 3.8+, QT5+, PSQL, SQLalchemy)
- ООП
- многопоточность (включая переопределение базового класса, очередь)
- ORM
- генераторы
- различные типы данных
- в БД применены: составной индекс, представления, триггерные функции и т.д.
- различные паттерны (MVC, Command, Observer, Adapter и др.)
- и т.п.

### Основное окно - список оборудования
![Image alt](https://github.com/RuslanV/pyqt_example/blob/main/screenshots/app_screenshot_1.png)

### Дочернее окно - редактирование/изменение/добавление оборудования
![Image alt](https://github.com/RuslanV/pyqt_example/blob/main/screenshots/app_screenshot_2.png)

### Для работы приложения необходима БД, которую можно запустить в docker.
Сборка контейнера:
```
docker run -d --name example_app_pgdb -e POSTGRES_PASSWORD=db_password -e POSTGRES_USER=db_user -e POSTGRES_DB=example_db -p 54321:5432 example_app_pgdb
```
