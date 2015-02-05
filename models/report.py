# -*- coding: utf-8 -*-
"""
    Модель отчетов поступающих с терминалов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app, cache
from sqlalchemy.sql import func

from helpers import date_helper

from models.base_model import BaseModel
from models.term import Term
from models.firm import Firm
from models.person import Person
from models.event import Event


class Report(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'report'

    TYPE_WHITE = 0
    TYPE_PAYMENT = 1
    TYPE_MPS = 2

    CORP_TYPE_OFF = 0
    CORP_TYPE_ON = 1

    DEFAULT_PAGE = 1
    POST_ON_PAGE = 10

    STATUS_COMPLETE = 1
    STATUS_NEW = 0
    STATUS_FAIL = -1
    STATUS_LOST = -2

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    name = db.Column(db.Text, nullable=False)
    payment_id = db.Column(db.String(20))
    term_firm_id = db.Column(db.Integer, nullable=False)
    person_firm_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    corp_type = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.amount = 0
        self.firm_id = 0
        self.person_firm_id = 0
        self.person_id = False
        self.corp_type = self.CORP_TYPE_OFF
        self.type = self.TYPE_WHITE
        self.name = 'Anonim'
        self.tz = app.config['TZ']
        self.order = 'creation_date desc'
        self.limit = self.POST_ON_PAGE
        self.page = self.DEFAULT_PAGE
        self.period = 'day'
        self.payment_type = self.TYPE_WHITE
        self.status = self.STATUS_NEW

    def add_new(self):
        from models.term_corp_wallet import TermCorpWallet

        error = False
        old_report = self.get_by_params()
        if old_report:
            return error

        self.status = self.STATUS_COMPLETE
        # Если операция платежная
        if int(self.type) == self.TYPE_PAYMENT:
            self.status = self.STATUS_NEW

        # Если операция по белому списку и есть корп кошелек, меняем его баланс
        if self.person_id and int(self.type) == Report.TYPE_WHITE:
            person = Person.query.get(self.person_id)

            if person.wallet_status == Person.STATUS_VALID and person.type == Person.TYPE_WALLET:

                self.corp_type = self.CORP_TYPE_ON
                corp_wallet = TermCorpWallet.query.filter_by(
                    person_id=person.id).first()

                if not corp_wallet:
                    return error

                corp_wallet.balance = int(
                    corp_wallet.balance) - int(
                        self.amount)
                corp_wallet.save()

        # Блокируем возможность платежей через корпоративный кошелек
                if corp_wallet.balance < TermCorpWallet.BALANCE_MIN:
                    person.wallet_status = Person.STATUS_BANNED
                    person.save()

        if not self.save():
            error = True

        return error

    @staticmethod
    def get_new_payment():
        return Report.query.filter_by(
            type=Report.TYPE_PAYMENT,
            status=Report.STATUS_NEW).all()

    @staticmethod
    def get_fail_payment():
        return Report.query.filter_by(
            type=Report.TYPE_PAYMENT,
            status=Report.STATUS_FAIL).all()

    def copy_new_from_old(self, new_balance=False):
        fields = self.__dict__.keys()
        fields.remove('id')
        fields.remove('_sa_instance_state')
        fields.remove('amount')

        new_report = Report()
        map(lambda field: setattr(new_report, field, getattr(self, field)), fields)
        new_report.status = Report.STATUS_NEW

        if new_balance:
            new_report.amount = abs(new_balance)
        else:
            new_report.amount = self.amount

        if new_report.save():
            return True
        return False

    def get_by_params(self):
        return Report.query.filter_by(term_id=self.term_id,
                                      event_id=self.event_id,
                                      creation_date=self.creation_date,
                                      payment_id=self.payment_id).first()

    def _get_search_params(self, **kwargs):
        keys = [
            'firm_id',
            'person_id',
            'type',
            'order',
            'limit',
            'page',
            'period',
            'payment_type']

        for key in keys:
            if key not in kwargs:
                continue
            setattr(self, key, kwargs[key])

        return True

    def _set_period_group(self, query, period):
        if period == 'day':
            return query.group_by(
                'YEAR(creation_date), MONTH(creation_date), DAY(creation_date)')
        if period == 'week':
            return query.group_by(
                'YEAR(creation_date), WEEK(creation_date, 1)')
        if period == 'month':
            return query.group_by('YEAR(creation_date), MONTH(creation_date)')

        return query

    def _set_firm_id_filter(self, query, firm_id, payment_type):
        if payment_type == self.TYPE_WHITE:
            query = query.filter(
                (Report.term_firm_id == firm_id) | (Report.person_firm_id == firm_id))
        else:
            query = query.filter(Report.term_firm_id == firm_id)
        return query

    def person_general_query(self, **kwargs):
        answer = {}
        self._get_search_params(**kwargs)

        query = db.session.query(Report.creation_date)

        if self.person_id:
            query = query.filter(Report.person_id == self.person_id)
        else:
            query = query.filter(Report.person_firm_id == self.firm_id)

        query = query.filter(Report.type == self.TYPE_WHITE)
        query = Report()._set_period_group(query, self.period)
        query = query.order_by(self.order)

        answer['reports_count'] = query.count()
        answer['reports'] = query.limit(
            self.limit).offset((self.page - 1) * self.limit).all()
        reports_all = query.all()
        answer['page_dates'] = []
        for row in reports_all:
            answer['page_dates'].append(row[0].strftime('%d.%m.%Y'))

        return answer

    def person_detaled_query(self, search_date):
        interval = date_helper.get_date_interval(search_date, self.period)
        query = Report.query.filter(Report.type == self.payment_type)
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        if self.person_id:
            query = query.filter(Report.person_id == self.person_id)
        else:
            query = query.filter(Report.person_firm_id == self.firm_id)

        query = query.filter(Report.type == self.TYPE_WHITE)
        query = query.order_by('creation_date desc')

        return query.all()

    #@cache.cached(timeout=30)
    def get_person_report(self, **kwargs):

        time_pattern = '%H:%M'
        date_pattern = '%d.%m.%Y'
        month_pattern = '%m.%Y'
        self._get_search_params(**kwargs)

        if self.period == 'day':
            result_date_pattern = date_pattern
        elif self.period == 'month':
            result_date_pattern = month_pattern

        answer = self.person_general_query(**kwargs)

        result = []
        events = Event.get_dict()
        term_name_dict = Term.select_name_dict()
        for report in answer['reports']:
            search_date = date_helper.from_utc(
                report[0],
                self.tz)
            creation_date = search_date.strftime(date_pattern)

            data = dict(
                creation_date=search_date.strftime(result_date_pattern),
                amount=0,
                count=0
            )

            data['page_dates'] = answer['page_dates']
            data['detaled'] = []
            detaled_reports = self.person_detaled_query(search_date)
            for row in detaled_reports:

                creation_date = date_helper.from_utc(
                    row.creation_date,
                    self.tz)

                term_name = 'Empty'
                if row.term_id in term_name_dict:
                    term_name = term_name_dict[row.term_id]

                detaled_data = dict(
                    id=row.id,
                    term=term_name,
                    time=creation_date.strftime(time_pattern),
                    date=creation_date.strftime(date_pattern),
                    event=events[
                        row.event_id] if events[
                            row.event_id] else 'Empty',
                    amount=float(row.amount) / 100,
                    name=row.name,
                )
                data['count'] += 1
                data['amount'] += detaled_data['amount']
                data['detaled'].append(detaled_data)

            result.append(data)

        value = dict(
            result=result,
            count=answer['reports_count'],
        )
        return value

    def term_general_query(self, **kwargs):
        answer = {}
        self._get_search_params(**kwargs)

        query = db.session.query(Report.creation_date)
        query = query.filter(Report.type == self.payment_type)

        query = Report()._set_firm_id_filter(
            query, self.firm_id, self.payment_type)

        query = Report()._set_period_group(query, self.period)
        query = query.order_by(self.order)

        answer['reports_count'] = query.count()
        answer['reports'] = query.limit(
            self.limit).offset((self.page - 1) * self.limit).all()

        return answer

    def term_detaled_query(self, search_date):
        interval = date_helper.get_date_interval(search_date, self.period)

        query = db.session.query(
            Report.term_id,
            Report.person_firm_id,
            func.sum(Report.amount),
            func.count(Report.id))
        query = query.filter(Report.type == self.payment_type)
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        query = Report()._set_firm_id_filter(
            query, self.firm_id, self.payment_type)
        query = query.group_by('term_id', 'person_firm_id').order_by('amount')

        return query.all()

    def get_date_pattern(self):
        date_pattern = False
        if self.period == 'month':
            date_pattern = '%m.%Y'
        elif self.period == 'week':
            date_pattern = '%x'
        else:
            date_pattern = '%d.%m.%Y'

        return date_pattern

    def format_search_date(self, search_date):
        from datetime import timedelta
        date_pattern = self.get_date_pattern()

        if isinstance(search_date, (tuple)):
            interval = (
                search_date[0].strftime('%d.%m.%Y'),
                search_date[1].strftime('%d.%m.%Y'))
            return '%s - %s' % interval

        if self.period == 'week':
            interval = date_helper.get_date_interval(
                search_date, self.period)
            interval = (
                interval[0].strftime('%d.%m.%Y'),
                (interval[1] - timedelta(days=1)).strftime('%d.%m.%Y'))
            creation_date = '%s - %s' % interval
        else:
            creation_date = search_date.strftime(date_pattern)

        return creation_date

    @cache.cached(timeout=30)
    def get_term_report(self, **kwargs):

        self._get_search_params(**kwargs)
        answer = self.term_general_query(**kwargs)

        result = []
        terms_name = Term.select_name_dict()
        firms_name = Firm.select_name_dict()
        for report in answer['reports']:
            search_date = date_helper.from_utc(report[0], self.tz)
            creation_date = self.format_search_date(search_date)

            data = {
                'creation_date': creation_date,
                'amount': 0,
                'count': 0
            }

            detaled_report = self.term_detaled_query(search_date)
            data['term'] = {}
            for row in detaled_report:
                term_name = terms_name[row[0]] if row[0] in terms_name else 'Empty'
                firm_name = firms_name[row[1]] if row[1] in firms_name else 'Empty'

                amount = float(row[2]) / 100
                count = int(row[3])

                if row[0] not in data['term']:
                    data['term'][row[0]] = {
                        'name': term_name,
                        'amount': 0,
                        'count': 0,
                        'firm': []
                    }

                data['term'][row[0]]['amount'] += amount
                data['term'][row[0]]['count'] += count

                data['term'][row[0]]['firm'].append(
                    {
                        'name': firm_name,
                        'amount': amount,
                        'count': count
                    }
                )

                data['count'] += count
                data['amount'] += amount

            result.append(data)

        value = dict(
            result=result,
            count=answer['reports_count'],
        )

        return value

    def term_query(self, interval):
        query = db.session.query(
            Report.term_id,
            Report.person_firm_id,
            func.count(Report.id),
            func.sum(Report.amount).label("summ1"))

        query = query.filter(Report.type == Report.TYPE_WHITE)
        query = query.filter(
            (Report.term_firm_id == self.firm_id) | (Report.person_firm_id == self.firm_id))
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        query = query.group_by(Report.term_id, Report.person_firm_id)
        query = query.order_by('summ1 desc')

        return query

    def corp_query(self, interval):
        query = db.session.query(
            Report.person_id,
            func.sum(Report.amount),
            Report.term_id)

        query = query.filter(Report.corp_type == Report.CORP_TYPE_ON)
        query = query.filter(Report.person_firm_id == self.firm_id)
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        query = query.group_by(Report.person_id, Report.term_id)
        query = query.order_by(Report.name)
        return query

    def person_query(self, interval):
        query = db.session.query(
            Report.person_id,
            func.sum(Report.amount),
            Report.term_id,
            Report.name)

        if self.person_id:
            query = query.filter(Report.person_id == self.person_id)

        query = query.filter(Report.type == Report.TYPE_WHITE)
        query = query.filter(Report.person_firm_id == self.firm_id)
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        query = query.group_by(Report.person_id, Report.term_id)
        query = query.order_by(Report.name)
        return query

    def money_query(self, interval):
        query = db.session.query(
            Report.term_id,
            func.count(Report.id),
            func.sum(Report.amount).label("summ1"))

        query = query.filter(Report.type == Report.TYPE_PAYMENT)
        query = query.filter(Report.term_firm_id == self.firm_id)
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        query = self._set_period_group(query, self.period)
        query = query.group_by(Report.term_id)
        query = query.order_by('summ1 desc')

        return query
