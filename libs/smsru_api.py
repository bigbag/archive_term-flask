# -*- coding: utf-8 -*-
"""
    Библиотека для работы с сервисом sms.ru

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import string
import csv
from console import app
from grab import Grab
from lxml import etree


class SmsruApi(object):

    def __init__(self, const):
        self.const = const
        self.token = None
        self.grab = None

    def get_url(self, method):
        return "%s%s" % (self.const.GENERAL_URL, self.const.METHODS[method])

    def set_request(self, url, data=None):
        return_data = False

        if not self.grab:
            self.grab = Grab()

        if data:
            self.grab.setup(post=data)

        try:
            self.grab.go(url)
        except Exception as e:
            app.logger.error(e)
        else:
            return_data = self.grab

        return return_data

    def get_token(self):
        """Получаем токен безопасности, время жизни 10 минут"""
        token = self.set_request(self.get_url('get_token'))
        self.token = token.response.body
        return True

    def get_sing(self):
        """Генерим код для повышения безопасности"""
        if not self.token:
            self.get_token()

        value = "%s%s" % (
            self.const.PASSWORD,
            self.token)
        return hashlib.sha512(value).hexdigest()

    def sms_send(self, to, text):
        """Отправляем смс"""

        if not self.token:
            self.get_token()

        data = dict(
            login=self.const.LOGIN,
            token=self.token,
            sha512=self.get_sing(),
            to=to,
            text=text
        )
        print data

        if self.const.PARTNER_ID:
            data['partner_id'] = self.const.PARTNER_ID

        return self.set_request(self.get_url('sms_send'), data)
