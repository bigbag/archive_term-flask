# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на оповещение о сбое

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class AlarmStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'alarm_stack'

    DEFAULT_COUNT = 1
    DEFAULT_INTERVAL = 86400

    LOCK_FREE = 0
    LOCK_SET = 1

    id = db.Column(db.Integer, primary_key=True)
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    emails = db.Column(db.Text, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    lock = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, firm_id=None, term_id=None):
        self.lock = self.LOCK_FREE
        self.interval = self.DEFAULT_INTERVAL
        self.count = self.DEFAULT_COUNT
        self.term_id = term_id
        self.firm_id = firm_id

    def get_term_alarm(self):
        alarm = AlarmStack.query.filter_by(
            term_id=self.term_id,
            firm_id=self.firm_id).first()
        if not alarm:
            alarm = self

        m, s = divmod(alarm.interval, 60)
        h, m = divmod(m, 60)
        alarm.interval = "%d:%02d" % (h, m)

        return alarm

    @staticmethod
    def reset_count(term_id):
        result = False
        alarm = AlarmStack.query.filter_by(term_id=term_id).first()
        if not alarm:
            return result

        alarm.count = AlarmStack.DEFAULT_COUNT
        if alarm.save():
            result = True

        return result

    def save(self):
        self.emails = self.encode_field(self.emails)

        return BaseModel.save(self)
