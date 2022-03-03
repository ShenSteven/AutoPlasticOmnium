#!/usr/bin/env python
# coding: utf-8
"""
@File   : setup.py.py
@Author : Steven.Shen
@Date   : 2021/12/8
@Desc   : 
"""
import os
import sys
import platform
import shutil
from setuptools import setup, Command, find_packages

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    current_path = sys._MEIPASS
else:
    current_path = os.path.dirname(os.path.abspath(__file__))

os_type = platform.system()
print(os_type + " detected!")

# # Checking dependencies!
# not_installed = ''
#
# # pyqt5
# try:
#     import PyQt5
#
#     print('python3-pyqt5 is found')
# except:
#     print('Error : python3-pyqt5 or pyside6 must be installed!')
#     not_installed = not_installed + '(PyQt5 or PySide6)'
#
# # python3-requests
# try:
#     import requests
#
#     print('python3-requests is found!')
# except:
#     print('Error : requests is not installed!')
#     not_installed = not_installed + 'python3-requests, '
#
# # psutil
# try:
#     import psutil
#
#     print('python3-psutil is found!')
# except:
#     print("Warning: python3-psutil is not installed!")
#     not_installed = not_installed + 'psutil, '
#
# # yaml
# try:
#     import yaml
#
#     print('python3-PyYAML is found!')
# except:
#     print("Warning: python3-PyYAML is not installed!")
#     not_installed = not_installed + 'PyYAML, '
#
# # logging
# try:
#     import logging
#
#     print('python3-logging is found!')
# except:
#     print("Warning: python3-logging is not installed!")
#     not_installed = not_installed + 'logging, '
#
# # show warning , if dependencies not installed!
# if not_installed != '':
#     print('########################')
#     print('####### WARNING ########')
#     print('########################')
#     print('Some dependencies are not installed .It causes some problems! : \n')
#     print(not_installed + '\n\n')
#     print('Read this link for more information: \n')
#     print('https://github.com/persepolisdm/persepolis/wiki/git-installation-instruction\n\n')
#     answer = input('Do you want to continue?(y/n)')
#     if answer not in ['y', 'Y', 'yes']:
#         sys.exit(1)

packages = ['conf', 'model', 'scripts', 'sockets', 'ui']

requires = [
    'PyQt5~=5.15.4',
    'PyYAML~=5.4.1',
    'requests~=2.26.0',
    'openpyxl~=3.0.7',
    'psutil~=5.8.0',
    'pyserial~=3.5',
    'setuptools~=57.0.0'
]
# test_requirements = [
#     'pytest-httpbin==0.0.7',
#     'pytest-cov',
#     'pytest-mock',
#     'pytest-xdist',
#     'PySocks>=1.5.6, !=1.5.7',
#     'pytest>=3'
# ]

about = {}
with open(os.path.join(current_path, 'conf', '__version__.py'), 'r', 'utf-8') as f:
    exec(f.read(), about)

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=packages,
    py_modules=['AutoTestSystem.py'],
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={'AutoTestSystem': 'AutoTestSystem'},
    include_package_data=True,
    python_requires=">=3.8, !=3.9.*",
    install_requires=requires,
    license=about['__license__'],
    zip_safe=False,
    # extras_require={
    #     'security': [],
    #     'socks': ['PySocks>=1.5.6, !=1.5.7'],
    #     'socks:sys_platform == "win32" and python_version == "2.7"': ['win_inet_pton'],
    #     'use_chardet_on_py3': ['chardet>=3.0.2,<5']
    # },
    project_urls={
        'Documentation': 'https://requests.readthedocs.io',
        'Source': 'https://github.com/psf/requests',
    },
)
