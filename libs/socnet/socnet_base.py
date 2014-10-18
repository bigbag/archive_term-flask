# -*- coding: utf-8 -*-
"""
    Базовый класс для библиотек работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""


class SocnetBase():
    CONDITION_PASSED = 1
    CONDITION_FAILED = 0
    CONDITION_ERROR = -1

    def dummy_control(self, loyalty_id):
        """заглушка для еще нериализованных в конкретной соцсети методов"""

        return False
