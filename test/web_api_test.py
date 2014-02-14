# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса api

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web


class WebApiTestCase(unittest.TestCase):

    API_URL = '/term/v1.0'
    GARBAGE_URL = '/123456'
    CALLBACK_CONFIG_URL = '/api/term/configs/callback/0000000021_config'
    CALLBACK_FAIL_CONFIG_URL = '/api/term/configs/callback/0000000021_1213'
    CALLBACK_BLACKLIST_URL = '/api/term/configs/callback/0000000021_blacklist'
    CALLBACK_VERSION_URL = '/api/term/configs/callback/0000000021_config_1.0m.316'
    BLACKLIST_URL = '/api/term/configs/blacklist.xml'
    TERM_URL = '/api/term/configs/config_0000000021.xml'
    FAIL_TERM_URL = '/api/term/configs/config_9999999999.xml'
    REPORT_URL = '/api/term/reports/report_0000000021_130903_164649.xml'
    TERM = '0000000021'

    REPORT_FILE = """<?xml version="1.0" encoding="windows-1251" standalone="yes" ?>
        <Report>
            <Event type="coffee">
                <Card time="11:37:02" date="2013-09-03" summ="2000" type="0">00777810000000021564</Card>
                <Card time="11:38:26" date="2013-09-03" summ="2000" type="0">00777810000000022306</Card>
                <Card time="11:40:25" date="2013-09-03" summ="2000" type="0">00777810000000021556</Card>
                <Card time="11:42:07" date="2013-09-03" summ="2000" type="0">00777810000000022257</Card>
            </Event>
        </Report>
        """

    FILE_SIGN = 'ivWdYrnPYTrNQ8J4lWiW2A=='

    def setUp(self):
        self.app = web.app.test_client()

    def test_404(self):
        rv = self.app.get(self.GARBAGE_URL)
        self.assertEqual(rv.status_code, 404)

    def test_config(self):
        rv = self.app.get(self.TERM_URL)
        self.assertEqual(rv.status_code, 200)

    def test_config_method(self):
        rv = self.app.post(self.TERM_URL)
        self.assertEqual(rv.status_code, 405)

    def test_config_fail_term_id(self):
        rv = self.app.post(self.FAIL_TERM_URL)
        self.assertEqual(rv.status_code, 405)

    def test_blacklist(self):
        rv = self.app.get(self.BLACKLIST_URL)
        self.assertEqual(rv.status_code, 200)

    def test_blacklist_method(self):
        rv = self.app.post(self.BLACKLIST_URL)
        self.assertEqual(rv.status_code, 405)

    def test_report(self):
        data = dict(upload_var=self.REPORT_FILE)
        headers = [('Content-MD5', self.FILE_SIGN)]

        rv = self.app.put(self.REPORT_URL, data=data, headers=headers)
        self.assertEqual(rv.status_code, 201)

    def test_report_metod(self):
        data = dict(upload_var=self.REPORT_FILE)
        headers = [('Content-MD5', self.FILE_SIGN)]

        rv = self.app.get(self.REPORT_URL, data=data, headers=headers)
        self.assertEqual(rv.status_code, 405)

    def test_report_headers(self):
        data = dict(upload_var=self.REPORT_FILE)
        rv = self.app.get(self.REPORT_URL, data=data)
        self.assertEqual(rv.status_code, 405)

    def test_callback_method(self):
        rv = self.app.get(self.CALLBACK_CONFIG_URL)
        self.assertEqual(rv.status_code, 405)

    def test_callback_fail_action(self):
        data = dict(
            term=self.TERM,
        )
        rv = self.app.post(self.CALLBACK_FAIL_CONFIG_URL, data=data)
        self.assertEqual(rv.status_code, 405)

    def test_callback_config(self):
        data = dict(
            type='config',
            term=self.TERM,
        )
        rv = self.app.post(self.CALLBACK_CONFIG_URL, data=data)
        self.assertEqual(rv.status_code, 201)

    def test_callback_blacklist(self):
        data = dict(
            type='blacklist',
            term=self.TERM,
        )
        rv = self.app.post(self.CALLBACK_BLACKLIST_URL, data=data)
        self.assertEqual(rv.status_code, 201)
