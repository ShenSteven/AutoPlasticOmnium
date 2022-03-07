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
# print(os_type + " detected!")

packages = ['src.conf']

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
with open(os.path.join(current_path, 'src/conf', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open(os.path.join(current_path, 'README.md'), 'r', encoding='utf-8') as f:
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
        packages=packages,
        py_modules=['src.py'],
        package_data={'': ['LICENSE', 'NOTICE']},
        package_dir={'': ''},
        include_package_data=True,
        python_requires=">=3.8, !=3.9.*",
        install_requires=requires,
        license=about['__license__'],
        zip_safe=False,
        project_urls={
            'Documentation': 'https://requests.readthedocs.io',
            'Source': 'https://github.com/psf/requests',
        },
    )
