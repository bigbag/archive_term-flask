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
import pycurl
import urllib
import logging
import cStringIO


class YaMoneyApi(object):

    CONNECT_TIMEOUT = 10
    TIMEOUT = 15

    def __init__(self, const):
        self.const = const
        self.curl = None
        self.instance_id = None
        self.success_uri = const.SUCCESS_URI
        self.fail_uri = const.FAIL_URI

        # logging.basicConfig(format=u'# %(levelname)s, file:%(filename)s,
        # line:%(lineno)d, time:%(asctime)s], error: %(message)s',
        # level=logging.INFO)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return "%s" % self.const

    def logging_status(self, status):
        error = ''
        if 'error' in status:
            error = status['error']
        info = "%s: %s" % (status['status'], error)

        self.logger.error(info)
        return True

    def get_random_headers(self):
        """
        Copyright: 2011, Grigoriy Petukhov
        Build headers which sends typical browser.
        """

        return {
            'Accept':
            'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Charset': 'utf-8,windows-1251;q=0.7,*;q=0.5',
            'Keep-Alive': '300',
            'Expect': '',
        }

    def get_url(self, method):
        general_url = self.const.GENERAL_URL
        if self.const.TEST:
            general_url = self.const.TEST_GENERAL_URL

        return "%s/%s" % (general_url, method)

    def init_request(self):
        if self.curl:
            return True

        headers = self.get_random_headers()
        header_tuples = [str('%s: %s' % x) for x
                         in headers.items()]

        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.HTTPHEADER, header_tuples)
        self.curl.setopt(pycurl.CONNECTTIMEOUT, self.CONNECT_TIMEOUT)
        self.curl.setopt(pycurl.TIMEOUT, self.TIMEOUT)
        self.curl.setopt(pycurl.NOSIGNAL, 1)

        if self.const.DEBUG:
            self.curl.setopt(pycurl.VERBOSE, 1)

        if self.const.CERTIFICATE_SECURITY:
            self.curl.setopt(pycurl.SSL_VERIFYPEER, 1)
            self.curl.setopt(pycurl.SSL_VERIFYHOST, 2)
            self.curl.setopt(
                pycurl.CAINFO,
                self.const.CERTIFICATE_PATH)
        else:
            self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        return True

    def set_request(self, url, data=None):
        if not self.init_request():
            self.logger.error('Fail in init pycurl')
            return False

        buf = cStringIO.StringIO()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buf.write)

        if data:
            if isinstance(data, dict):
                data = urllib.urlencode(data)
            self.curl.setopt(pycurl.POSTFIELDS, data)

        try:
            self.curl.perform()
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            return buf.getvalue()

    def _parse_result(self, result):
        try:
            result = json.loads(result)
        except Exception as e:
            self.logger.error(e)

        return result

    def get_instance_id(self):
        """Регистрация экземпляра приложения"""

        if self.const.INSTANCE_ID:
            return self.const.INSTANCE_ID

        if self.instance_id:
            return self.instance_id

        data = dict(client_id=self.const.CLIENT_ID)
        result = self.set_request(self.get_url('instance-id'), data)
        if not result:
            self.logger.error('Fail in instance-id request')
            return False

        result = self._parse_result(result)
        if not 'status' in result:
            self.logger.error('Not found field status')
            return False

        if result['status'] != 'success':
            self.logging_status(status)
            return False

        self.instance_id = result['instance_id']
        return self.instance_id

    def _request_external_payment(self, method, data):
        instance_id = self.get_instance_id()
        if not instance_id:
            return False

        data['instance_id'] = instance_id
        result = self.set_request(self.get_url(method), data)
        if not result:
            return False

        result = self._parse_result(result)

        return result

    def get_request_payment_p2p(self, amount, recipient, message=None):
        """Создание перевода на кошелек"""

        data = dict(
            pattern_id='p2p',
            amount=amount,
            to=recipient,
            message=message
        )

        result = self._request_external_payment(
            'request-external-payment', data)
        if not result:
            return False

        if not 'status' in result:
            self.logger.error('Not found field status')
            return False

        if result['status'] != 'success':
            return False

        return result

    def get_request_payment_to_shop(self, amount, pattern_id, order_id=0):
        """Создание платежа в магазин"""

        data = dict(
            pattern_id=pattern_id,
            sum=amount,
            customerNumber=order_id
        )

        result = self._request_external_payment(
            'request-external-payment', data)
        if not result:
            return False

        if not 'status' in result:
            self.logger.error('Not found field status')
            return False

        if result['status'] != 'success':
            return False

        return result

    def get_process_external_payment(self, request_id, token=False):
        """Проведение платежа получение информации о статусе платежа"""

        data = dict(
            request_id=request_id,
            ext_auth_success_uri=self.success_uri,
            ext_auth_fail_uri=self.fail_uri,
        )
        if not token:
            data['request_token'] = True
        if token:
            data['money_source_token'] = token

        result = self._request_external_payment(
            'process-external-payment', data)
        return result

    def get_linking_card_params(self, order_id=0):
        """Запрос параметров для привязки карты"""

        payment = self.get_request_payment_to_shop(
            1, self.const.CARD_PATTERN_ID, order_id)
        if not payment:
            return False

        status = self.get_process_external_payment(payment['request_id'])
        if not 'status' in status:
            self.logger.error('Not found field status')
            return False

        if status['status'] != 'ext_auth_required':
            self.logging_status(status)
            return False

        if not 'acs_uri' in status or not 'acs_params' in status:
            self.logger.error('Not found fields acs_uri or acs_params')
            return False

        result = dict(
            url=status['acs_uri'],
            params=status['acs_params']
        )

        return result

    def get_payment_info(self, request_id):
        """
            Получаем платежный информацию для фоновых платежей и отображения привязанной карты
            в интерфейсе
        """

        status = self.get_process_external_payment(request_id)
        if not status or not 'status' in status:
            self.logger.error('Not found fields status')
            return False

        if status['status'] not in ('success', 'in_progress'):
            self.logging_status(status)
            return False

        result = dict(
            invoice_id=status['invoice_id'],
            request_id=request_id
        )
        if 'money_source' in status:
            result['token'] = status['money_source']['money_source_token']
            result['card_pan'] = status['money_source']['pan_fragment']
            result['card_type'] = status['money_source']['payment_card_type']

        return result

    def background_payment(self, amount, token):
        """Фоновый платеж по карте"""

        payment = self.get_request_payment_to_shop(
            amount, self.const.PAYMENT_PATTERN_ID)

        if not payment:
            return False

        status = self.get_process_external_payment(
            payment['request_id'], token)

        status['request_id'] = payment['request_id']

        if status['status'] not in ('success', 'in_progress'):
            self.logging_status(status)
            return False

        return status
