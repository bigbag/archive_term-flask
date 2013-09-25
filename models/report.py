# -*- coding: utf-8 -*-
"""
    Модель отчетов поступающих с терминалов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import time
from web import db, app, cache
from sqlalchemy.sql import func

from helpers import date_helper

from models.term import Term
from models.person import Person
from models.firm import Firm
from models.event import Event
from models.firm_term import FirmTerm


class Report(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'report'

    TYPE_WHITE = 0
    TYPE_PAYMENT = 1
    TYPE_MPS = 2

    DATE_PATTERN = "%Y-%m-%d %H:%M:%S"

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    payment_id = db.Column(db.String(20))
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    check_summ = db.Column(db.String(32), nullable=False)

    def __init__(self):
        self.amount = 0
        self.person_id = 0
        self.firm_id = 0
        self.type = self.TYPE_WHITE

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_db_view(self, data):
        self.payment_id = str(data.text).rjust(20, '0')

        persons = Person.query.filter_by(
            payment_id=self.payment_id).all()

        firm_id_list = FirmTerm().get_list_by_term_id(self.term.id)
        for person in persons:
            if person.firm_id in firm_id_list:
                self.person_id = person.id
                self.firm_id = person.firm_id
                continue

        if data.get('summ'):
            self.amount = data.get('summ')

        if data.get('type'):
            self.type = data.get('type')

        date_time = "%s %s" % (
            data.get('date'),
            data.get('time'))

        date_time_utc = date_helper.convert_date_to_utc(
            date_time,
            self.term.tz,
            self.DATE_PATTERN,
            self.DATE_PATTERN)
        self.creation_date = date_time_utc
        self.check_summ = self.get_check_summ()
        return self

    def get_by_check_summ(self, check_summ):
        return self.query.filter_by(check_summ=check_summ).first()

    @cache.cached(timeout=120, key_prefix='report_person')
    def select_person(self, firm_id, **kwargs):
        tz = app.config['TZ']
        date_pattern = '%H:%M %d.%m.%y'

        order = kwargs[
            'order'] if 'order' in kwargs else 'creation_date desc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        query = Report.query.filter(Report.firm_id == firm_id).filter(
            Report.type == self.TYPE_WHITE).order_by(order)

        reports_count = query.count()
        reports = query.paginate(page, limit, False).items

        result = []
        for report in reports:

            creation_date = date_helper.from_utc(
                report.creation_date,
                tz)
            creation_date = creation_date.strftime(date_pattern)

            term = Term.query.get(report.term_id)
            data = dict(
                id=report.id,
                term=term.name if term else 'Empty',
                creation_date=creation_date,
                event=report.event.name if report.event else 'Empty',
                first_name=report.person.first_name if report.person else '',
                midle_name=report.person.midle_name if report.person else '',
                last_name=report.person.last_name if report.person else '',
            )
            result.append(data)

        value = dict(
            report=result,
            count=reports_count,
        )

        return value

    def get_select_summ_query(self, firm_id, **kwargs):
        answer = {}

        order = kwargs['order'] if 'order' in kwargs else 'creation_date desc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1
        detaled = kwargs['detaled'] if 'detaled' in kwargs else False
        period = kwargs['period'] if 'period' in kwargs else 'all'

        firm_term = FirmTerm().get_list_by_firm_id(firm_id)

        if not period == 'all':
            query = db.session.query(
                Report.creation_date,
                Report.event_id,
                Report.term_id,
                func.sum(Report.amount),
                func.count(Report.amount))

            if detaled:
                query = query.group_by('term_id')

            query = query.group_by(
                'YEAR(creation_date), MONTH(creation_date)')

            if period == 'day':
                query = query.group_by('DAY(creation_date)')
            elif period == 'week':
                query = query.group_by('WEEK(creation_date)')
        else:
            query = db.session.query(
                Report.creation_date,
                Report.event_id,
                Report.term_id,
                Report.amount)

        query = query.filter(
            Report.term_id.in_(
                firm_term)).filter(
                    Report.type == self.TYPE_PAYMENT)

        query = query.order_by(order)
        query = query.order_by('term_id asc')

        answer['reports_count'] = query.count()
        answer['reports'] = query.limit(limit).offset((page - 1) * limit).all()

        return answer

    #@cache.cached(timeout=120, key_prefix='report_summ')
    def select_summ(self, firm_id, **kwargs):
        tz = app.config['TZ']
        detaled = kwargs['detaled'] if 'detaled' in kwargs else False

        date_pattern = '%H:%M %d.%m.%y'
        if 'period' in kwargs:
            period = kwargs['period']

            if period == 'day':
                date_pattern = '%d.%m.%Y'
            elif period == 'month':
                date_pattern = '%m.%Y'
            elif period == 'week':
                date_pattern = '%W, %m.%Y'
            elif detaled:
                date_pattern = '%H:%M %d.%m.%y'

        answer = self.get_select_summ_query(firm_id, **kwargs)

        result = []
        for report in answer['reports']:

            creation_date = date_helper.from_utc(
                report[0],
                tz)
            creation_date = creation_date.strftime(date_pattern)

            term = Term.query.get(report[2])
            event = Event.query.get(report[1])

            data = dict(
                creation_date=creation_date,
                amount=int(report[3] / 100),
                count=report[4] if 4 in report else 1,
                term=term.name if term else 'Empty',
                event=event.name if event else 'Empty',
            )

            result.append(data)

        value = dict(
            report=result,
            count=answer['reports_count'],
        )

        return value

    def get_check_summ(self):
        return hashlib.md5("%s%s%s%s%s" % (
            str(self.term_id),
            str(self.event_id),
            str(self.type),
            str(self.creation_date),
            str(self.payment_id))).hexdigest()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            self.payment_id = str(self.payment_id).rjust(20, '0')
            if not self.check_summ:
                self.check_summ = self.get_check_summ()
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
