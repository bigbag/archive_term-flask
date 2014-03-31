# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на генерацию отчета

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


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
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    email = db.Column(db.Text, nullable=False)
    excel = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, index=True, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text)
    launch_date = db.Column(db.DateTime)
    lock = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.excel = self.EXCEL_YES
        self.type = TYPE_PERSON
        self.interval = INTERVAL_ONCE
        self.lock = self.LOCK_FREE

    def get_interval_list(self):
        return [
            {'id': self.INTERVAL_ONCE, 'name': u"Разовый"},
            {'id': self.INTERVAL_DAY, 'name': u"Дневной"},
            {'id': self.INTERVAL_WEEK, 'name': u"Недельный"},
            {'id': self.INTERVAL_MONTH, 'name': u"Месячный"}
        ]

    def get_type_list(self):
        return [
            {'id': self.TYPE_PERSON, 'name': u"По людям"},
            {'id': self.TYPE_TERM, 'name': u"По терминалам"},
            {'id': self.TYPE_MONEY, 'name': u"Личные расходы"}
        ]

    def get_json(self):
        self.email = json.loads(self.email)
        self.recipients = json.loads(self.recipients)
        return self
