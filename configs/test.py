# -*- coding: utf-8 -*-
"""
    Тестовые настройки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""


class Config(object):
    DEBUG = False
    TESTING = False

    CACHE_TYPE = 'NullCache'

    SQLALCHEMY_BINDS = {
        'term': 'sqlite://',
        'stack': 'sqlite://',
        'payment': 'sqlite://',
        'payment_old': 'sqlite://',
        'mobispot': 'sqlite://'
    }

    SQLALCHEMY_ECHO = False

    SECRET_KEY = 'null'
