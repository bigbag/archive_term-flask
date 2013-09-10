# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web
from helpers import hash_helper


class WebApiAdminTestCase(unittest.TestCase):

    GENERATE_URL = '/api/admin/spot/generate'
    LINKING_URL = '/api/admin/spot/linking'
    FREE_URL = '/api/admin/spot/free'
    INFO_URL = '/api/admin/spot/1259038160727942'
    EAN = '0076969992007'
    PIDS = '0077781000'
    HID = 1259038160727942

    ADMIN_KEY = '7131b1e8722240660480dfbb99592cb030debfa9'
    ADMIN_SECRET = 'cb81b4036eb381e528062a582725b1ec4d91650664e78a26c30a8147'

    def setUp(self):
        self.app = web.app.test_client()

    def test_spot_generate(self):
        data = dict(
            count=1,
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.GENERATE_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 200)

    def test_spot_generate_metod(self):
        data = dict(
            count=1,
        )
        rv = self.app.get(self.GENERATE_URL, data=data)
        self.assertEqual(rv.status_code, 405)

    def test_spot_linking(self):
        data = dict(
            hid=self.HID,
            pids=self.PIDS,
            ean=self.EAN
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 200)

    def test_spot_info(self):

        data = dict()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]

        rv = self.app.get(self.INFO_URL, headers=headers)
        self.assertEqual(rv.status_code, 200)
