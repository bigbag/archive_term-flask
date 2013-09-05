# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web


class WebApiAdminTestCase(unittest.TestCase):

    GENERATE_URL = '/term/admin/spot/generate'
    LINKING_URL = '/term/admin/spot/linking'
    FREE_URL = '/term/admin/spot/free'
    INFO_URL = '/term/admin/spot/1259038160727942'
    EAN = '0076969992007'
    PIDS = '0077781000'
    HID = 1259038160727942

    def setUp(self):
        self.app = web.app.test_client()

    def test_spot_generate(self):
        data = dict(
            count=1,
        )
        rv = self.app.post(self.GENERATE_URL, data=data)
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
        rv = self.app.post(self.LINKING_URL, data=data)
        self.assertEqual(rv.status_code, 200)

    def test_spot_info(self):
        rv = self.app.get(self.INFO_URL)
        self.assertEqual(rv.status_code, 200)

    def test_spot_info(self):
        rv = self.app.get(self.FREE_URL)
        self.assertEqual(rv.status_code, 200)
