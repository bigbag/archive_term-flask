# -*- coding: utf-8 -*-
"""
    Настройки отправки смс через сервис sms.ru

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""


class SmsruConfig(object):
    GENERAL_URL = 'http://sms.ru/'

    METHODS = dict(
        get_token='auth/get_token',
        sms_send='sms/send',
        sms_status='sms/status',
        sms_cost='sms/cost',
        get_balance='my/balance',
        get_limit='my/limit',
        auth_check='auth/check',
    )

    API_ID = 'ef54993c-5809-7d14-a9d0-608af8694836'
    LOGIN = '79627056382'
    PASSWORD = '33,fytvtn'
    # API_ID = 'b36758fc-2236-4a64-799d-85645315d7a0'
    PARTNER_ID = 29386
    SENDER_NAME = False
