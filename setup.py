from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='pyqt_example',
    version='1.0',
    packages=find_packages(),
    description='Пример кода одного из модулей',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
)