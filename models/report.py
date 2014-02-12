# -*- coding: utf-8 -*-
"""
    Модель отчетов поступающих с терминалов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import time
from datetime import datetime, timedelta
from web import db, app, cache
from sqlalchemy.sql import func

from flask import g

from helpers import date_helper

from models.term import Term
from models.person import Person
from models.event import Event
from models.firm_term import FirmTerm


class Report(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'report'

    TYPE_WHITE = 0
    TYPE_PAYMENT = 1
    TYPE_MPS = 2

    CORP_TYPE_OFF = 0
    CORP_TYPE_ON = 1

    DEFAULT_PAGE = 1
    POST_ON_PAGE = 10

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), index=True)
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), index=True)
    person = db.relationship('Person')
    name = db.Column(db.Text, nullable=False)
    payment_id = db.Column(db.String(20))
    term_firm_id = db.Column(db.Integer, nullable=False)
    person_firm_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    corp_type = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.amount = 0
        self.person_id = 0
        self.person_firm_id = 0
        self.firm_id = 0
        self.corp_type = self.CORP_TYPE_OFF
        self.type = self.TYPE_WHITE
        self.name = 'Anonim'
        self.tz = app.config['TZ']
        self.order = 'creation_date desc'
        self.limit = self.POST_ON_PAGE
        self.page = self.DEFAULT_PAGE
        self.period = 'day'
        self.payment_type = self.TYPE_WHITE

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_db_view(self, data):
        date_pattern = '%Y-%m-%d %H:%M:%S'
        self.payment_id = str(data.text).rjust(20, '0')

        firm_id_list = FirmTerm().get_list_by_term_id(self.term.id)
        for firm_id in firm_id_list:
            person = Person.query.filter_by(
                payment_id=self.payment_id, firm_id=firm_id).first()
            if not person:
                continue

            self.name = person.name
            self.person_id = person.id
            self.person_firm_id = person.firm_id
            break

        firm_term = FirmTerm().query.filter_by(
            term_id=self.term.id).first()
        self.term_firm_id = firm_term.firm_id

        if data.get('summ'):
            self.amount = int(data.get('summ')) * int(self.term.factor)

        if data.get('type'):
            self.type = data.get('type')

        date_time = "%s %s" % (
            data.get('date'),
            data.get('time'))

        date_time_utc = date_helper.convert_date_to_utc(
            date_time,
            self.term.tz,
            date_pattern,
            date_pattern)
        self.creation_date = date_time_utc
        return self

    def get_by_params(self):
        return self.query.filter_by(term_id=self.term_id,
                                    event_id=self.event_id,
                                    creation_date=self.creation_date,
                                    payment_id=self.payment_id).first()

    def _get_search_params(self, **kwargs):

        keys = ['order', 'limit', 'page', 'period', 'payment_type']

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

    @cache.cached(timeout=120, key_prefix='report_person')
    def get_person_report(self, **kwargs):

        time_pattern = '%H:%M'
        date_pattern = '%d.%m.%Y'
        self._get_search_params(**kwargs)

        if 'person' in kwargs['type']:
            query = Report.query.filter(
                Report.person_id == kwargs['id']).order_by(
                    self.order)
        elif 'firm' in kwargs['type']:
            query = Report.query.filter(Report.person_firm_id == kwargs['id']).filter(
                Report.type == self.TYPE_WHITE).order_by(self.order)

        reports_count = query.count()
        reports = query.paginate(self.page, self.limit, False).items

        result = []
        events = Event().get_events_list()
        for report in reports:

            creation_date = date_helper.from_utc(
                report.creation_date,
                self.tz)

            term = Term().get_by_id(report.term_id)
            data = dict(
                id=report.id,
                term=term.name if term else 'Empty',
                term_id=term.id if term else 'Empty',
                date=creation_date.strftime(date_pattern),
                time=creation_date.strftime(time_pattern),
                event=events[
                    report.event_id] if events[
                        report.event_id] else 'Empty',
                amount=float(report.amount) / 100,
                name=report.name,
            )
            result.append(data)

        value = dict(
            result=result,
            count=reports_count,
        )

        return value

    def interval_query(self, firm_id, **kwargs):
        answer = {}
        self._get_search_params(**kwargs)

        query = db.session.query(
            Report.creation_date,
            func.sum(Report.amount),
            func.count(Report.id))

        query = query.filter(Report.type == self.payment_type)
        query = Report()._set_firm_id_filter(query, firm_id, self.payment_type)
        query = Report()._set_period_group(query, self.period)
        query = query.order_by(self.order)

        answer['reports_count'] = query.count()
        answer['reports'] = query.limit(
            self.limit).offset((self.page - 1) * self.limit).all()

        return answer

    def interval_detaled_query(self, firm_id, search_date):
        interval = date_helper.get_date_interval(search_date, self.period)

        query = db.session.query(
            Report.term_id,
            func.sum(Report.amount),
            func.count(Report.id))
        query = query.filter(Report.type == self.payment_type)
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))

        query = Report()._set_firm_id_filter(query, firm_id, self.payment_type)
        query = query.group_by('term_id').order_by('amount')

        return query.all()

    # @cache.cached(timeout=60, key_prefix='report_interval')
    def get_firm_interval_report(self, firm_id, **kwargs):
        payment_type = self.TYPE_WHITE

        if 'payment_type' in kwargs:
            payment_type = kwargs['payment_type']

        period = kwargs['period'] if 'period' in kwargs else 'day'
        if period == 'day':
            date_pattern = '%d.%m.%Y'
        elif period == 'month':
            date_pattern = '%m.%Y'
        elif period == 'week':
            date_pattern = '%x'

        answer = self.interval_query(firm_id, **kwargs)

        result = []
        for report in answer['reports']:

            search_date = date_helper.from_utc(
                report[0],
                self.tz)

            if period == 'week':
                interval = date_helper.get_date_interval(search_date, period)
                interval = (
                    interval[0].strftime('%d.%m.%Y'),
                    interval[1].strftime('%d.%m.%Y'))
                creation_date = '%s - %s' % interval
            else:
                creation_date = search_date.strftime(date_pattern)

            data = dict(
                creation_date=creation_date,
                amount=float(report[1]) / 100,
                count=int(report[2])
            )

            detaled_report = self.interval_detaled_query(firm_id, search_date)
            data['detaled'] = []

            for row in detaled_report:

                term = Term().get_by_id(row[0])
                detaled_data = dict(
                    term=term.name if term else 'Empty',
                    amount=float(row[1]) / 100,
                    count=int(row[2])
                )
                data['detaled'].append(detaled_data)

            result.append(data)

        value = dict(
            result=result,
            count=answer['reports_count'],
        )

        return value

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            self.payment_id = str(self.payment_id).rjust(20, '0')
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
