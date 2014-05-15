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

    SUCCESS_REQUEST_ID = '3535393131395f63643332316436666634653437633539376331396663393231623862366637663533626465656461'

    def setUp(self):
        self.app = web.app.test_client()

        self.ym = YaMoneyApi(YandexMoneyConfig)
        self.ym.const.TEST = True
        self.ym.const.DEBUG = False
        self.ym.const.CERTIFICATE_SECURITY = False

    def test_url_generator(self):
        assert self.ym.get_url('test')

    def test_init_request(self):
        assert self.ym.init_request()

    def test_set_request(self):
        self.ym = YaMoneyApi(YandexMoneyConfig)
        self.ym.const.CERTIFICATE_SECURITY = True
        assert self.ym.set_request(self.ym.const.GENERAL_URL)

    def test_fail_ssl_set_request(self):
        self.ym = YaMoneyApi(YandexMoneyConfig)
        self.ym.const.CERTIFICATE_SECURITY = True
        assert not self.ym.set_request('https://google.com')

    def test_instance_id_getter(self):
        assert self.ym.get_instance_id()

    def test_request_payment_to_shop(self):
        assert self.ym.get_request_payment_to_shop(self.PAYMENT_AMOUNT,
                                                   self.ym.const.CARD_PATTERN_ID)

    def test_request_payment_p2p(self):
        assert self.ym.get_request_payment_p2p(self.PAYMENT_AMOUNT,
                                               self.RECIPIENT_ID)

    def test_faled_request_payment_p2p(self):
        assert not self.ym.get_request_payment_p2p(self.PAYMENT_AMOUNT,
                                                   self.FALED_RECIPIENT_ID)

    def test_process_payment_to_shop(self):
        payment = self.ym.get_request_payment_to_shop(self.PAYMENT_AMOUNT,
                                                      self.ym.const.CARD_PATTERN_ID)
        assert payment
        assert self.ym.get_process_external_payment(payment['request_id'])

    def test_process_payment_to_p2p(self):
        payment = self.ym.get_request_payment_p2p(
            self.PAYMENT_AMOUNT, self.RECIPIENT_ID)
        assert payment
        assert self.ym.get_process_external_payment(payment['request_id'])

    def test_linking_card_params(self):
        assert self.ym.get_linking_card_params()

    def test_payment_token(self):
        assert self.ym.get_payment_info(self.SUCCESS_REQUEST_ID
                                        )

    def test_background_payment(self):
        payment_info = self.ym.get_payment_info(self.SUCCESS_REQUEST_ID)
        assert payment_info
        self.ym.background_payment(self.PAYMENT_AMOUNT, payment_info['token'])
