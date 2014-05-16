# -*- coding: utf-8 -*-
"""
    Задачи связанные с платежами

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import app
from web.celery import celery


class PaymentTask (object):

    @staticmethod
    @celery.task
    def linking_card():
        return True
