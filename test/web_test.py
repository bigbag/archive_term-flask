# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web


class WebTestCase(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

    def assert_status_code(self, url, code):
        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

    def test_config(self):
        url = '/term/v1.0/configs/config_0000000021.xml'
        self.assert_status_code(url, 200)

    def test_blacklist(self):
        url = '/term/v1.0/configs/blacklist.xml'
        self.assert_status_code(url, 200)
