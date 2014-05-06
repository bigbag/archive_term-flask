# -*- coding: utf-8 -*-
"""
    Библиотека для работы с сервисом ЯД

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import hashlib
import json
import string
import csv

from grab import Grab

from flask import current_app


class YaMoneyApi(object):

    def __init__(self, const, app=False):
        self.app = app and app or current_app._get_current_object()
        self.const = const
        self.grab = None
        self.instance_id = None

    def set_request(self, url, data=None):
        if not self.grab:
            self.grab = Grab()

        if data:
            self.grab.setup(post=data)

        try:
            self.grab.go(url)
        except Exception as e:
            self.app.logger.error(e)
        else:
            return self.grab
        return False

    def __repr__(self):
        return "%s" % self.const

    def get_url(self, method):
        general_url = self.const.GENERAL_URL
        if self.const.TEST:
            general_url = self.const.TEST_GENERAL_URL

        return "%s/%s" % (general_url, method)

    def _parse_result(self, result):
        try:
            result = json.loads(result.response.body)
        except Exception as e:
            self.app.logger.error(e)

        return result

    def get_instance_id(self):
        """Регистрация экземпляра приложения"""

        if self.instance_id:
            return self.instance_id

        data = dict(client_id=self.const.CLIENT_ID)
        result = self.set_request(self.get_url('instance-id'), data)
        result = self._parse_result(result)
        if result['status'] != 'success':
            return False

        self.instance_id = result['instance_id']

        return self.instance_id

    def _request_external_payment(self, data):
        instance_id = self.get_instance_id()
        if not instance_id:
            return False

        data['instance_id'] = instance_id
        result = self.set_request(self.get_url('request-external-payment'), data)
        result = self._parse_result(result)

        if result['status'] != 'success':
            return False

        return result

    def get_request_payment_to_shop(self, amount, pattern_id, message=None):
        """Создание платежа в магазин"""

        data = dict(
            instance_id=self.get_instance_id(),
            pattern_id=pattern_id,
            amount=amount,
            message=message
        )

        return self._request_external_payment(data)

    def get_request_payment_p2p(self, amount, recipient, message=None):
        """Создание перевода на кошелек"""

        data = dict(
            pattern_id='p2p',
            amount=amount,
            to=recipient,
            message=message
        )

        return self._request_external_payment(data)
