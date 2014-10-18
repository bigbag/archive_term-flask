# -*- coding: utf-8 -*-
"""
    Библиотека для работы с сервисом sms.ru

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import time
from grab import Grab

from console import app


class SmsruApi(object):
    SUCCESS_STATUS = 100
    SEND_STATUS = {
        100: "Message accepted",
        201: "Out of money",
        202: "Bad recipient",
        203: "Message text not specified",
        204: "Bad sender (unapproved)",
        205: "Message too long",
        206: "Day message limit reached",
        207: "Can't send messages to that number",
        208: "Wrong time",
        209: "Blacklisted recipient",
        210: "Bad method! Use GET, where you must use POST",
        211: "Method not found",
        212: "Message to be transmitted in UTF-8 (you passed in a different encoding)",
        220: "The service is temporarily unavailable, please try later.",
        230: "One phone on the day you can not send more than 250 messages",
        300: "Wrong token",
        301: "Wrong password or user not found",
        302: "The user is authenticated, but the account is not certified"
    }

    STATUS_STATUS = {
        -1: "Message not found",
        100: "Message is in the queue",
        101: "Message is on the way to the operator",
        102: "Message is on the way to the recipient",
        103: "Message delivered",
        104: "Message failed: out of time",
        105: "Message failed: cancelled by the operator",
        106: "Message failed: phone malfunction",
        107: "Message failed, reason unknown",
        108: "Message declined",
    }

    COST_STATUS = {
        100: "Success"
    }

    def __init__(self, const):
        self.const = const
        self._grab = None
        self._token = None
        self._token_ts = 0

    def _get_url(self, method):
        return "%s%s" % (self.const.GENERAL_URL, self.const.METHODS[method])

    def _set_request(self, url, data=None):
        return_data = False

        if not self._grab:
            self._grab = Grab()

        if data:
            self._grab.setup(post=data)

        try:
            self._grab.go(url)
        except Exception as e:
            app.logger.error(e)
        else:
            return_data = self._grab

        return return_data

    def _get_token(self):
        """Получаем токен безопасности, время жизни 10 минут"""
        if self._token_ts < time.time() - 500:
            self._token = None
        if self._token is None:
            self._token = self._set_request(
                self._get_url('get_token')).response.body
            self._token_ts = time.time()
        return self._token

    def _get_sing(self):
        """Генерим хеш от пароля и токена для повышения безопасности"""

        value = "%s%s" % (
            self.const.PASSWORD,
            self._token)
        return hashlib.sha512(value).hexdigest()

    def sms_send(self, to, text):
        """Отправляем смс"""
        data = dict(
            login=self.const.LOGIN,
            token=self._get_token(),
            sha512=self._get_sing(),
            to=to,
            text=text.encode("utf-8")
        )

        if self.const.PARTNER_ID:
            data['partner_id'] = self.const.PARTNER_ID

        if self.const.SENDER_NAME:
            data['from'] = self.const.SENDER_NAME

        result = self._set_request(
            self._get_url('sms_send'),
            data).response.body.split("\n")
        code = int(result[0])
        if code == self.SUCCESS_STATUS:
            return True
        else:
            messages = "%s %s" % (code, self.SEND_STATUS[code])
            app.logger.error(messages)
            return False
