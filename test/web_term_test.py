# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web
from models.term_user import TermUser


class WebTermTestCase(unittest.TestCase):

    GARBAGE_URL = '/term/123456'
    LOGIN_URL = '/term/login'
    LOGOUT_URL = '/term/logout'
    FORGOT_URL = '/term/forgot'
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

    def login(self, email, password):
        headers = [
            ('Content-Type', 'application/json;charset=utf-8'),
            ('Host', 'sodexo.mobispot.com')
        ]
        data = '{"email":"' + email + \
            '","password":"' + password + '"}'
        return self.app.post(self.LOGIN_URL,
                             data=data,
                             headers=headers,
                             follow_redirects=True)

    def logout(self):
        headers = [
            ('Host', 'sodexo.mobispot.com')
        ]
        return self.app.get(self.LOGOUT_URL, headers=headers, follow_redirects=True)

    def test_404(self):
        rv = self.app.get(self.GARBAGE_URL)
        self.assertEqual(rv.status_code, 404)

    def test_login_form(self):
        headers = [
            ('Host', 'sodexo.mobispot.com')
        ]
        rv = self.app.get(
            self.LOGIN_URL,
            headers=headers,
            follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

    def test_forgot(self):
        rv = self.app.get(self.FORGOT_URL)
        self.assertEqual(rv.status_code, 200)

    def test_login_logout(self):
        rv = self.login('', self.PASSWORD)
        assert 'error' in rv.data

        rv = self.login(self.EMAIL, self.BAD_PASSWORD)
        assert 'error' in rv.data

        rv = self.login(self.BAD_EMAIL, self.PASSWORD)
        assert 'error' in rv.data

        rv = self.login(self.EMAIL, self.PASSWORD)
        self.assertEqual(rv.status_code, 200)

        rv = self.logout()
        self.assertEqual(rv.status_code, 200)
