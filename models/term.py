# -*- coding: utf-8 -*-
"""
    Модель для платежных и вендинговых терминалов


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import g
from web import app, db, cache

from helpers import date_helper

from models.firm_term import FirmTerm
from models.term_event import TermEvent
from models.person_event import PersonEvent


class Term(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'term'

    STATUS_VALID = 1
    STATUS_BANNED = 0

    BLACKLIST_ON = 1
    BLACKLIST_OFF = 0

    TYPE_POS = 0
    TYPE_VENDING = 1

    SEANS_ALARM = 86400

    DEFAULT_FACTOR = 100

    id = db.Column(db.Integer, primary_key=True)
    hard_id = db.Column(db.Integer, unique=True)
    type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    tz = db.Column(db.String(300), nullable=False)
    blacklist = db.Column(db.Integer)
    settings_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, index=True)
    report_date = db.Column(db.DateTime)
    config_date = db.Column(db.DateTime)
    blacklist_date = db.Column(db.DateTime)
    upload_start = db.Column(db.String(256))
    upload_stop = db.Column(db.String(256))
    upload_period = db.Column(db.Integer, nullable=False)
    download_start = db.Column(db.String(256))
    download_stop = db.Column(db.String(256))
    download_period = db.Column(db.Integer, nullable=False)
    factor = db.Column(db.Integer)
    update_qid = db.Column(db.String(128))
    keyload_qid = db.Column(db.String(128))

    def __init__(self):
        self.type = self.TYPE_VENDING
        self.upload_start = "00:01"
        self.upload_stop = "23:59"
        self.upload_period = 5
        self.download_start = "00:01"
        self.download_stop = "23:59"
        self.download_period = 5
        self.tz = app.config['TZ']
        self.blacklist = self.BLACKLIST_OFF
        self.settings_id = 1
        self.factor = 1
        self.status = self.STATUS_VALID

    def __repr__(self):
        return '<id %r>' % (self.id)

    def term_add(self, firm_id):
        result = False

        if self.save():
            firm_term = FirmTerm()
            firm_term.term_id = self.id
            firm_term.firm_id = firm_id
            firm_term.child_firm_id = firm_id
            firm_term.save()
            result = True
        return result

    def term_remove(self):
        FirmTerm().query.filter_by(term_id=self.id).delete()
        TermEvent().query.filter_by(term_id=self.id).delete()
        PersonEvent().query.filter_by(term_id=self.id).delete()
        self.delete()

        return True

    def get_type_list(self):
        return [
            {'id': self.TYPE_VENDING, 'name': u"Вендинговый"},
            {'id': self.TYPE_POS, 'name': u"Платежный"}
        ]

    def get_blacklist_list(self):
        return [
            {'id': self.BLACKLIST_ON, 'name': u"Денежный"},
            {'id': self.BLACKLIST_OFF, 'name': u"Корпоративный"}
        ]

    def get_valid_term(self, hard_id):
        return self.query.filter_by(
            hard_id=hard_id,
            status=self.STATUS_VALID).first()

    def get_by_hard_id(self, hard_id):
        return self.query.filter_by(
            hard_id=int(hard_id)).first()

    def get_by_id(self, id):
        return self.query.filter_by(
            id=int(id)).first()

    def get_info_by_id(self, id):
        date_pattern = '%H:%M %d.%m.%y'
        term = Term().query.get(id)
        if term.report_date:
            term.report_date = date_helper.from_utc(
                term.report_date,
                term.tz).strftime(date_pattern)

        if term.config_date:
            term.config_date = date_helper.from_utc(
                term.config_date,
                term.tz).strftime(date_pattern)

        if term.blacklist_date:
            term.blacklist_date = date_helper.from_utc(
                term.blacklist_date,
                term.tz).strftime(date_pattern)
        return term

    def get_xml_view(self):
        self.tz = date_helper.get_timezone(self.tz)

        if self.type == self.TYPE_VENDING:
            self.type = 'Vending'
        elif self.type == self.TYPE_POS:
            self.type = 'Normal'
        return self

    def get_db_view(self):
        term = Term()
        if len(self.upload_start) == 0:
            self.upload_start = term.upload_start
        if len(self.download_start) == 0:
            self.download_start = term.download_start
        return self

    @cache.cached(timeout=60, key_prefix='term_name_dict')
    def select_name_dict(self):
        terms = Term.query.all()

        result = {}
        for term in terms:
            result[term.id] = term.name

        return result

    def select_term_list(self, firm_id, **kwargs):
        tz = app.config['TZ']
        date_pattern = '%H:%M %d.%m.%y'

        order = kwargs['order'] if 'order' in kwargs else 'id desc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        firm_term = FirmTerm().get_list_by_firm_id(firm_id)
        g.firm_term = firm_term

        query = Term.query.filter(Term.id.in_(firm_term))
        terms = query.paginate(page, limit, False).items

        result = []
        for term in terms:
            firm_general = FirmTerm().query.filter_by(term_id=term.id).first()

            seans_date = None
            seans_alarm = 0
            if term.config_date:
                delta = date_helper.get_curent_date(
                    format=False) - term.config_date

                seans_alarm = delta.total_seconds() > self.SEANS_ALARM

                seans_date = date_helper.from_utc(term.config_date, tz)
                seans_date = seans_date.strftime(date_pattern)
            data = dict(
                id=term.id,
                hard_id=term.hard_id,
                name=term.name,
                firm=firm_general.firm.name,
                status=int(term.status == self.STATUS_VALID),
                seans_date=seans_date,
                seans_alarm=int(seans_alarm),
            )

            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )

        return value

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
