# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web


class WebTestCase(unittest.TestCase):

    API_URL = '/term/v1.0'
    BLACKLIST_URL = '/term/v1.0/configs/blacklist.xml'
    TERM_URL = '/term/v1.0/configs/config_0000000021.xml'
    REPORT_URL = '/term/v1.0/reports/report_0000000021_130903_164649.xml'

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

    FILE_SIGN = 'jGM1aVidBxLjUmKajs4PuQ=='

    def setUp(self):
        self.app = web.app.test_client()

    def assert_status_code(self, url, code):
        rv = self.app.get(url)
        self.assertEqual(rv.status_code, 200)

    def test_config(self):
        self.assert_status_code(self.TERM_URL, 200)

    def test_blacklist(self):
        self.assert_status_code(self.BLACKLIST_URL, 200)

    def test_config(self):
        data = dict(
            username=1,
            password=2,
            upload_var=self.REPORT_FILE,
        )
        headers = [('Content-MD5', self.FILE_SIGN)]

        rv = self.app.put(self.REPORT_URL, data=data, headers=headers)
        self.assertEqual(rv.status_code, 201)

        print rv.data
