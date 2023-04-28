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
from os.path import abspath, join, dirname

# os_type = platform.system()
# print(os_type + " detected!")

requires = [
    'PyQt5~=5.15.4',
    'PyYAML~=5.4.1',
    'requests~=2.26.0',
    'openpyxl~=3.0.7',
    'psutil~=5.8.0',
    'pyserial~=3.5',
    'setuptools~=57.0.0'
]

about = {}
with open(join(dirname(abspath(__file__)), 'src', rf'conf{os.sep}__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open(join(dirname(abspath(__file__)), 'README.md'), 'r', encoding='utf-8') as f:
    readme = f.read()

if __name__ == "__main__":
    setup(
        name=about['__title__'],
        version=about['__version__'],
        description=about['__description__'],
        long_description=readme,
        long_description_content_type='text/markdown',
        author=about['__author__'],
        author_email=about['__author_email__'],
        url=about['__url__'],
        packages=find_packages('src'),
        package_data={'': ['LICENSE', 'NOTICE']},
        package_dir={'': 'src'},
        include_package_data=True,
        python_requires=">=3.8, !=3.9.*",
        install_requires=requires,
        license=about['__license__'],
        # zip_safe=False,
        # project_urls={
        #     'Documentation': 'https://requests.readthedocs.io',
        #     'Source': 'https://github.com/psf/requests', },
        entry_points={'console_scripts': ['autotest = src.__main__']}
    )
