#!/usr/bin/env python

from setuptools import setup

setup(name='plannord',
      version='0.1',
      description='Site du Plan Nord (version Bruno)',
      author='Jonathan Villemaire-Krajden',
      author_email='odontomachus@gmail.com',
      install_requires = [
          'tornado',
          'sqlalchemy',
          'mysql-connector-python',
        ]
     )
