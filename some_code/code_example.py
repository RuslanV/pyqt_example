# -*- coding: utf-8 -*-


"""
Примеры кода к наиболее часто задаваемым вопросам.
"""

# "Декораторы" - это что? Примеры использования. Как написать параметризованный декоратор?
import time

def timer(func):
    """
    Пример декоратора для замера времени выполнения функции.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Время выполнения функции {func.__name__}: {end_time - start_time}")
        return result
    return wrapper

@timer
def my_function():
    pass
    # код функции

def repeat(n):
    """
    Декоратор с параметром.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for i in range(n):
                print(f"Результат выполнения функции {func.__name__}: {result}")
            return result
        return wrapper
    return decorator

# Для использования декоратора с параметром нужно указать параметры при вызове декоратора-фабрики, например:
@repeat(3)
def my_function():
    return 42


# Можно ли в питоне реализовать синглтоновский класс (класс, имеющий только один объект одновременно)?
# С использованием декоратора:
def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@singleton
class MyClass:
    pass

# С использованием метакласса:
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class MyClass(metaclass=Singleton):
    pass

# С использованием модуля:
class MySingleton:
    pass

my_singleton = MySingleton() # В этом случае экземпляр класса создается при импорте модуля, и в других модулях, которые импортируют данный модуль, можно использовать уже созданный экземпляр.
