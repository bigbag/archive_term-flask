# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на оповещение о сбое

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import json

from web import db

from models.base_model import BaseModel

from helpers import hash_helper


class AlarmStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'alarm_stack'

    id = db.Column(db.Integer, primary_key=True)
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    emails = db.Column(db.Text, nullable=False)
    interval = db.Column(db.Integer, nullable=False)

    def get_term_alarm(self, term_id, firm_id):
        term_alarm = {'emails': None, 'interval': None}
        alarm = AlarmStack.query.filter_by(
            term_id=term_id, firm_id=firm_id).first()
        if alarm:
            term_alarm['emails'] = alarm.emails
            hours = str(alarm.interval / (60 * 60))
            if len(hours) == 1:
                hours = '0' + hours
            minutes = str((alarm.interval % (60 * 60)) / 60)
            if len(minutes) == 1:
                minutes = '0' + minutes
            term_alarm['interval'] = hours + ':' + minutes

        return term_alarm
