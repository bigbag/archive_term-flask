# -*- coding: utf-8 -*-
"""
    Настройки платежных систем

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""


class UnitellerConfig(object):
    GENERAL_URL = 'wpay.uniteller.ru'

    METHOD = (
        'pay',
        'results',
        'unblock',
        'recurrent',

    )

    TEST = False
    TEST_PREFIX = 'https://test.'
    DEFAULT_PREFIX = 'https://'

    TIME_PAID_CHANGE = 14
    CODE_SUCCES = 'AS000'

    SHOP_ID = '00001623'
    PASSWORD = 'kl9Gu1PJyE0yKfNdhCOiTtQnBPFlNNnirGhaw1qY8cm4zVbZXKg79QAvUPnrZqydvcOBua6t1En1Fl3E'
    LOGIN = 813
