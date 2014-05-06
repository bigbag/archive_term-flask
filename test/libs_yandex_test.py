# -*- coding: utf-8 -*-
"""
    Тест библиотеки yandex апи

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi


class LibsYandexTestCase(unittest.TestCase):

    FALED_CLIENT_ID = 'wewewerwer'
    FALED_PATTERN_ID = 99999

    RECIPIENT_ID = 4100322629324
    FALED_RECIPIENT_ID = 4100111111111

    PAYMENT_AMOUNT = 100

    def setUp(self):
        self.app = web.app.test_client()
        self.ym = YaMoneyApi(YandexMoneyConfig, self.app)
        self.CLIENT_ID = self.ym.const.CLIENT_ID
        self.ym.const.TEST = True

    def test_url_generator(self):
        ym = self.ym
        assert ym.get_url('test')

    def test_instance_id_getter(self):
        assert self.ym.get_instance_id()

    def test_faled_instance_id_getter(self):
        self.ym.const.CLIENT_ID = self.FALED_CLIENT_ID
        assert not self.ym.get_instance_id()
        self.ym.const.CLIENT_ID = self.CLIENT_ID

    def test_faled_request_payment_to_shop(self):
        assert not self.ym.get_request_payment_to_shop(self.PAYMENT_AMOUNT,
                                                       self.FALED_PATTERN_ID)

    def test_request_payment_p2p(self):
        assert self.ym.get_request_payment_p2p(self.PAYMENT_AMOUNT, self.RECIPIENT_ID)

    def test_faled_request_payment_p2p(self):
        assert not self.ym.get_request_payment_p2p(self.PAYMENT_AMOUNT,
                                                   self.FALED_RECIPIENT_ID)
