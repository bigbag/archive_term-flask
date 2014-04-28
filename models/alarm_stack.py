# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на оповещение о сбое

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel

from helpers import hash_helper


class AlarmStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'alarm_stack'

    DEFAULT_COUNT = 1
    DEFAULT_INTERVAL = 86400

    id = db.Column(db.Integer, primary_key=True)
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    emails = db.Column(db.Text, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, firm_id=None, term_id=None):
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

    def reset_count(self, term_id):
        result = False
        alarm = self.query.filter_by(term_id=term_id)
        if not alarm:
            return result

        alarm.count = DEFAULT_COUNT
        if alarm.save():
            result = True

        return result

    def save(self):
        self.emails = self.encode_field(self.emails)

        return BaseModel.save(self)
