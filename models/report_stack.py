# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на генерацию отчета

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json

from web import db

from models.base_model import BaseModel

from helpers import hash_helper


class ReportStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'report_stack'

    LOCK_FREE = 0
    LOCK_SET = 1

    EXCEL_NO = 0
    EXCEL_YES = 1

    INTERVAL_ONCE = 0
    INTERVAL_DAY = 1
    INTERVAL_WEEK = 2
    INTERVAL_MONTH = 3

    TYPE_PERSON = 0
    TYPE_TERM = 1
    TYPE_MONEY = 2

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    emails = db.Column(db.Text, nullable=False)
    excel = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, index=True, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text)
    launch_date = db.Column(db.DateTime)
    check_summ = db.Column(db.Text, nullable=False)
    lock = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.excel = self.EXCEL_YES
        self.type = self.TYPE_PERSON
        self.interval = self.INTERVAL_ONCE
        self.lock = self.LOCK_FREE

    def get_interval_list(self):
        return [
            {'id': self.INTERVAL_ONCE, 'name': u"Один раз"},
            {'id': self.INTERVAL_DAY, 'name': u"Ежедневно"},
            {'id': self.INTERVAL_WEEK, 'name': u"Еженедельно"},
            {'id': self.INTERVAL_MONTH, 'name': u"Ежемесячно"}
        ]

    def interval_meta(self):
        return {
            self.INTERVAL_ONCE: 'once',
            self.INTERVAL_DAY: 'day',
            self.INTERVAL_WEEK: 'week',
            self.INTERVAL_MONTH: 'month'
        }

    def get_interval_meta(self, interval):
        interval_meta = self.interval_meta()
        if interval in interval_meta:
            return interval_meta[interval]
        return False

    def get_sender_interval_list(self):
        return {
            self.INTERVAL_ONCE: u"Однократный",
            self.INTERVAL_DAY: u"Ежедневный",
            self.INTERVAL_WEEK: u"Еженедельный",
            self.INTERVAL_MONTH: u"Ежемесячный"
        }

    def get_sender_interval_name(self, interval):
        interval_name = self.get_sender_interval_list()
        if interval in interval_name:
            return interval_name[interval]
        return False

    def get_type_list(self):
        return [
            {'id': self.TYPE_PERSON, 'name': u"По людям"},
            {'id': self.TYPE_TERM, 'name': u"По терминалам"},
            {'id': self.TYPE_MONEY, 'name': u"Личным расходам"}
        ]

    def get_sender_type_list(self):
        return {
            self.TYPE_PERSON: u"Корпоративные расходы, люди",
            self.TYPE_TERM: u"Корпоративные расходы, терминалы",
            self.TYPE_MONEY: u"Личные расходы",
        }

    def get_sender_type_name(self, type):
        type_name = self.get_sender_type_list()
        if type in type_name:
            return type_name[type]
        return False

    def type_meta(self):
        return {
            self.TYPE_PERSON: 'person',
            self.TYPE_TERM: 'term',
            self.TYPE_MONEY: 'money',
        }

    def get_type_meta(self):
        type_meta = self.type_meta()
        if self.type in type_meta:
            return type_meta[self.type]
        return False

    def get_excel_list(self):
        return [
            {'id': self.EXCEL_YES, 'name': u"Да"},
            {'id': self.EXCEL_NO, 'name': u"Нет"},
        ]

    def get_json(self):
        self.email = json.loads(self.email)
        self.recipients = json.loads(self.recipients)
        return self

    def set_check_summ(self):
        data = [
            str(self.firm_id),
            str(self.emails),
            str(self.excel),
            str(self.type),
            str(self.interval)]

        data = '&'.join(data)
        self.check_summ = hash_helper.get_content_md5(data)
        return True

    def save(self):
        if not self.check_summ:
            self.set_check_summ()

        if not self.id:
            self.emails = str(json.dumps(self.emails))

        if self.details and not isinstance(self.emails, str):
            self.details = str(json.dumps(self.details))
        return BaseModel.save(self)
