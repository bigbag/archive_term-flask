# -*- coding: utf-8 -*-
"""
    Модель для платежных и вендинговых терминалов


    :copyright: (c) 2015 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import logging
from flask import g
from web import app, db, cache
from sqlalchemy import desc

from helpers import date_helper

from models.base_model import BaseModel
from models.firm_term import FirmTerm
from models.term_event import TermEvent
from models.person_event import PersonEvent


class Term(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'term'

    STATUS_VALID = 1
    STATUS_BANNED = 0

    BLACKLIST_ON = 1
    BLACKLIST_OFF = 0

    TYPE_POS = 0
    TYPE_VENDING = 1

    AUTH_PID = 'pid'
    AUTH_HID = 'uid'

    SEANS_ALARM = 86400
    USED_LAST_MONTH = 1728000

    DEFAULT_FACTOR = 100

    log = logging.getLogger('model')

    id = db.Column(db.Integer, primary_key=True)
    hard_id = db.Column(db.Integer, unique=True)
    type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    tz = db.Column(db.String(300), nullable=False)
    blacklist = db.Column(db.Integer)
    auth = db.Column(db.String(16))
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
    update_period = db.Column(db.Integer, nullable=False)
    update_force_on_restart = db.Column(db.Integer, nullable=False)
    keyload_qid = db.Column(db.String(128))
    has_gprs = db.Column(db.Integer)
    has_comission = db.Column(db.Integer)
    transaction_on_term = db.Column(db.Integer)

    def __init__(self):
        self.type = self.TYPE_VENDING
        self.upload_start = "00:01"
        self.upload_stop = "23:59"
        self.upload_period = 5
        self.update_period = 999999999
        self.update_force_on_restart = 0
        self.download_start = "00:01"
        self.download_stop = "23:59"
        self.download_period = 5
        self.tz = app.config['TZ']
        self.blacklist = self.BLACKLIST_OFF
        self.auth = self.AUTH_PID
        self.settings_id = 1
        self.factor = 1
        self.update_qid = 1
        self.status = self.STATUS_VALID
        self.has_gprs = 1
        self.has_comission = 1
        self.transaction_on_term = 0

    def save(self):
        if self.auth == self.AUTH_HID:
            self.blacklist = self.BLACKLIST_OFF

        return BaseModel.save(self)

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
        from models.payment_history import PaymentHistory
        from models.payment_fail import PaymentFail
        from models.report import Report

        try:
            FirmTerm.query.filter_by(term_id=self.id).delete(False)
            TermEvent.query.filter_by(term_id=self.id).delete(False)
            PersonEvent.query.filter_by(term_id=self.id).delete(False)

            reports = Report.query.filter_by(term_id=self.id).all()
            reports_id = list(set([report.id for report in reports]))
            Report.query.filter_by(term_id=self.id).delete(False)

            if reports_id:
                PaymentHistory.query.filter(
                    PaymentHistory.report_id.in_(reports_id)).delete(False)
                PaymentFail.query.filter(
                    PaymentFail.report_id.in_(reports_id)).delete(False)

            self.delete(False)

            db.session.commit()
        except Exception as e:
            self.log.error(e)
            db.session.rollback()
            return False
        else:
            return True

    def get_type_list(self):
        return [
            {'id': self.TYPE_VENDING, 'name': u"Вендинговый"},
            {'id': self.TYPE_POS, 'name': u"POS-терминал"}
        ]

    def get_factor_list(self):
        return [
            {'id': 1, 'name': u"Копейки"},
            {'id': 100, 'name': u"Рубли"}
        ]

    def get_auth_list(self):
        return [
            {'id': self.AUTH_PID, 'name': u"По pid карты"},
            {'id': self.AUTH_HID, 'name': u"По uid карты"}
        ]

    def get_blacklist_list(self):
        return [
            {'id': self.BLACKLIST_ON, 'name':
                u"Корпоративные и реальные деньги"},
            {'id': self.BLACKLIST_OFF, 'name': u"Корпоративные деньги"}
        ]

    @staticmethod
    def get_valid_term(hard_id):
        return Term.query.filter_by(
            hard_id=hard_id,
            status=Term.STATUS_VALID).first()

    @staticmethod
    def get_by_hard_id(hard_id):
        return Term.query.filter_by(
            hard_id=int(hard_id)).first()

    @staticmethod
    def get_by_id(id):
        return Term.query.filter_by(
            id=int(id)).first()

    @staticmethod
    def get_info_by_id(id):
        date_pattern = '%H:%M %d.%m.%y'
        term = Term.query.get(id)
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

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='all_terms_type_dict')
    def select_name_dict():
        terms = Term.query.all()

        result = {}
        for term in terms:
            result[term.id] = term.name

        return result

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='terms_tz_type_dict')
    def select_tz_dict():
        terms = Term.query.all()

        result = {}
        for term in terms:
            result[term.id] = term.tz

        return result
        
        
    @staticmethod
    def select_term_list(firm_id, **kwargs):
        date_pattern = '%H:%M %d.%m.%y'

        order = kwargs['order'] if 'order' in kwargs and kwargs[
            'order'] else 'config_date'
        order_desc = kwargs['order_desc'] if 'order_desc' in kwargs else True
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        firm_term = FirmTerm.get_list_by_firm_id(firm_id)
        g.firm_term = firm_term

        query = Term.query.filter(Term.id.in_(firm_term))

        if order:
            if order_desc:
                query = query.order_by(desc(order))
            else:
                query = query.order_by(order)

        terms = query.paginate(page, limit, False).items

        result = []
        for term in terms:
            firm_general = FirmTerm.query.filter_by(term_id=term.id).first()

            seans_date = None
            seans_alarm = 0
            if term.config_date:
                delta = date_helper.get_current_date(
                    format=False) - term.config_date

                seans_alarm = delta.total_seconds() > Term.SEANS_ALARM

                seans_date = date_helper.from_utc(term.config_date, term.tz)
                seans_date = seans_date.strftime(date_pattern)
            data = dict(
                id=term.id,
                hard_id=term.hard_id,
                name=term.name,
                firm=firm_general.firm.name,
                status=int(term.status == Term.STATUS_VALID),
                seans_date=seans_date,
                seans_alarm=int(seans_alarm),
                tz=term.tz,
            )

            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )

        return value
