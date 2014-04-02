# -*- coding: utf-8 -*-
"""
    Базовый класс для библиотек работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from grab import Grab
import json


class SocnetBase():
    TOKEN_NOT_SHARED = -1  # для тестов
    TOKEN_FOR_SHARED = -2  # для тестов
