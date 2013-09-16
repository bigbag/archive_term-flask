# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса админского api

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web
from models.term_user import TermUser


class WebTermTestCase(unittest.TestCase):

    GARBAGE_URL = '/term/123456'
    LOGIN_URL = '/term/login'
    EMAIL = 'test@test.ru'
    PASSWORD = '12345678'
    BAD_EMAIL = 'test123@test.ru'
    BAD_PASSWORD = '123456'

    def setUp(self):
        user = TermUser()
        user.email = self.EMAIL
        user.password = self.PASSWORD
        user.status = TermUser.STATUS_ACTIVE
        user.save()
        self.app = web.app.test_client()

    def tearDown(self):
        user = TermUser().get_by_email(self.EMAIL)
        user.delete()

    def test_404(self):
        rv = self.app.get(self.GARBAGE_URL)
        self.assertEqual(rv.status_code, 404)

    def test_login(self):
        rv = self.app.get(self.LOGIN_URL)
        self.assertEqual(rv.status_code, 200)

    def test_login_request_empty_email(self):
        data = '"password":"' + self.PASSWORD + '"}'
        headers = [
            ('Content-Type', 'application/json;charset=utf-8'),
        ]
        rv = self.app.post(self.LOGIN_URL, data=data)
        self.assertEqual(rv.status_code, 400)

    def test_login_request_bad_password(self):
        data = '{"email":"' + self.EMAIL + \
            '","password":"' + self.BAD_PASSWORD + '"}'
        headers = [
            ('Content-Type', 'application/json;charset=utf-8'),
        ]
        rv = self.app.post(self.LOGIN_URL, data=data)
        self.assertEqual(rv.status_code, 403)

    def test_login_request_bad_email(self):
        data = '{"email":"' + self.BAD_EMAIL + \
            '","password":"' + self.PASSWORD + '"}'
        headers = [
            ('Content-Type', 'application/json;charset=utf-8'),
        ]
        rv = self.app.post(self.LOGIN_URL, data=data)
        self.assertEqual(rv.status_code, 403)

    def test_login_request(self):
        data = '{"email":"' + self.EMAIL + \
            '","password":"' + self.PASSWORD + '"}'
        headers = [
            ('Content-Type', 'application/json;charset=utf-8'),
        ]
        rv = self.app.post(self.LOGIN_URL, data=data)
        self.assertEqual(rv.status_code, 200)
