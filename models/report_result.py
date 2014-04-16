# -*- coding: utf-8 -*-
"""
    Модель сводных отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
from datetime import datetime, timedelta

from web import app

from models.term import Term
from models.firm import Firm
from models.report import Report
from models.report_stack import ReportStack

from helpers import date_helper


class ReportResult(object):

    def __init__(self, task):
        self.task = task
        self.firm = self.get_firm()
        self.interval = self.get_interval_dict()
        self.type = self.get_type_dict()
        self.report = self.get_report()
        self.terms = {}
        self.persons = []
        self.data = {}
        self.all = dict(summ=0, count=0)

    def get_firm(self):
        result = None
        if self.task and self.task.firm_id:
            firm = Firm.query.get(self.task.firm_id)
        return firm

    def get_report_file(self):
        return "%s/excel%s_%s.xlsx" % (app.config['EXCEL_FOLDER'],
                                       self.firm.id, int(time.time()))

    def get_interval_dict(self):
        result = {}
        if not self.task:
            return None

        result['meta'] = ReportStack().get_interval_meta(self.task.interval)
        result['templ_name'] = ReportStack().get_sender_interval_name(
            self.task.interval)
        result['date'] = datetime.now() - timedelta(1)
        result['search'] = date_helper.get_date_interval(
            result['date'], result['meta'])

        if self.task.interval == ReportStack.INTERVAL_ONCE:
            interval = self.task.decode_field(self.task.details)
            result['search'] = (datetime.strptime(interval['start'], '%Y-%m-%d'), datetime.strptime(interval['end'], '%Y-%m-%d'))
            result['date'] = result['search']

        report = Report()
        report.period = result['meta']
        result['templ_interval'] = report.format_search_date(result['date'])

        return result

    def get_type_dict(self):
        result = {}
        if not self.task:
            return None

        result['meta'] = ReportStack().get_type_meta(self.task.type)
        result['templ_name'] = ReportStack().get_sender_type_name(
            self.task.type)

        return result

    def get_report(self):
        if not self.task or not self.firm:
            return False
        if not self.type or not self.type['meta']:
            return False
        if not self.interval or not self.interval['meta'] or not self.interval['search']:
            return False

        report = Report()
        report.firm_id = self.firm.id
        report.period = self.interval['meta']

        report_query_name = "%s_query" % self.type['meta']
        if report_query_name not in Report.__dict__:
            return False

        return getattr(report, report_query_name)(self.interval['search']).all()

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
