# -*- coding: utf-8 -*-
"""
    Задача отправки смс

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from web.celery import celery

from libs.smsru_api import SmsruApi
from configs.smsru import SmsruConfig


@celery.task
def send(phone, text):
    sms = SmsruApi(SmsruConfig)
    return sms.sms_send(phone, text)
