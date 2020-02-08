#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
  name             = 'fabric-chef',
  version          = '0.0.1',
  description      = 'Useful Fabric tasks for Chef operations.',
  license          = 'MIT',
  author           = 'Yohei TSUJI',
  url              = 'https://github.com/crossroad0201/fabric-chef',
  keywords         = 'fabric chef',
  packages         = find_packages(),
  install_requires = [
    'fabric<2.0',
    'prettytable'
  ]
)
