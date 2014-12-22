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
        self.person_id = self.get_person_id()
        self.data = {}
        self.all = dict(summ=0, count=0)

    def get_firm(self):
        if self.task and self.task.firm_id:
            firm = Firm.query.get(self.task.firm_id)
        return firm

    def get_report_file(self):
        return "%s/excel%s_%s.xlsx" % (app.config['EXCEL_FOLDER'],
                                       self.firm.id, int(time.time()))

    def get_person_id(self):
        result = False
        if not self.task:
            return False

        details = self.task.details
        if details and 'person' in details:
            details = self.task.decode_field(details)
            result = details['person']

        return result

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

        full_format = '%Y-%m-%d %H:%M:%S'
        simple_format = '%Y-%m-%d'
        if self.task.interval == ReportStack.INTERVAL_ONCE:
            details = self.task.details
            if details and 'period' in details:
                details = self.task.decode_field(details)
                interval = details['period']
                try:
                    result['search'] = (
                        date_helper.to_utc(
                            datetime.strptime(interval['start'], full_format), app.config['TZ']),
                        date_helper.to_utc(
                            datetime.strptime(interval['end'], full_format), app.config['TZ']))
                except:
                    result['search'] = (
                        date_helper.to_utc(
                            datetime.strptime(interval['start'], simple_format), app.config['TZ']),
                        date_helper.to_utc(
                            datetime.strptime(interval['end'], simple_format), app.config['TZ']))

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
        report.person_id = self.get_person_id()

        report_query_name = "%s_query" % self.type['meta']
        if report_query_name not in Report.__dict__:
            return False

        return getattr(report, report_query_name)(self.interval['search']).all()

    @staticmethod
    def get_corp_keys():
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
            amount=u'Итого, руб.'
        )

    @staticmethod
    def get_person_keys():
        return (
            'name',
            'tabel_id',
            'card',
            'amount')

    @staticmethod
    def get_corp_col_name():
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
        terms = Term.select_name_dict()
        if term_id not in self.terms:

            self.terms[term_id] = dict(
                name=terms[term_id],
                amount=0
            )
        return True
