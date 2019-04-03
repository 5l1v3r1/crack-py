#!/usr/bin/env python

from setuptools import setup, find_packages

setup (name = "crack",
       version = "0.3",
       license = "GPL",
       description='Simple Facebook account cracker',
       author = "val (zvtyrdt.id)",
       author_email = "xnver404@gmail.com",
       url = "https://github.com/zevtyardt",
       py_modules = ['crack'],
       packages=find_packages(),
       include_package_data=True,
       zip_safe=False,
       entry_points={'console_scripts': ['crack=crack.crack:main']}
)