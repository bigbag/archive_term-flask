# -*- coding: utf-8 -*-
"""
    Модель отчетов для отправки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from models.term import Term


class ReportSender(object):

    def __init__(self):
        self.data = {}
        self.all_summ = 0
        self.all_count = 0
        self.persons = []
        self.terms = {}
        self.interval = False
        self.interval_name = False
        self.type_name = False
        self.firm_id = False
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
            amount=u'Итого, руб.'
        )

    @staticmethod
    def get_money_keys():
        return (
            'term_name',
            'count',
            'amount')

    @staticmethod
    def get_money_col_name():
        return dict(
            term_name=u'Терминал',
            count=u'Количество',
            amount=u'Итого, руб.',
        )

    def set_terms(self, term_id):
        terms = Term().select_name_dict()
        if term_id not in self.terms:
            if term_id not in self.terms:
                term_name = u'Не известно'
            if term_id in terms:
                term_name = terms[term_id]

            self.terms[term_id] = dict(
                name=terms[term_id],
                amount=0
            )
        return True
