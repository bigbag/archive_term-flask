# -*- coding: utf-8 -*-
"""
    Модель отчетов для отправки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""


class ReportSender(object):

    def __init__(self):
        self.data = {}
        self.summ = 0
        self.persons = []
        self.terms = {}
        self.interval = False
        self.interval_name = False
        self.firm_name = False
        self.col_keys = {}
        self.col_name = {}

    @staticmethod
    def get_person_keys():
        return (
            'name',
            'tabel_id',
            'card',
            'wallet_interval',
            'wallet_limit',
            'amount')

    @staticmethod
    def get_person_col_name():
        return dict(
            name=u'ФИО',
            tabel_id=u'Таб. номер',
            card=u'Карта',
            wallet_interval=u'Статус кошелька',
            wallet_limit=u'Размер кошелька, руб',
            amount=u'Итого'
        )
