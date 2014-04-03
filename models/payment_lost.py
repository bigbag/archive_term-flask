# -*- coding: utf-8 -*-
"""
    Модель для потерянных операций

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib

from web import db

from models.base_model import BaseModel
from models.term import Term
from models.event import Event


class PaymentLost(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'lost'

    TYPE_WHITE = 0
    TYPE_PAYMENT = 1

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), index=True)
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    payment_id = db.Column(db.String(20))
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.amount = 0
        self.type = self.TYPE_WHITE

    def add_lost_payment(self, report):
        self.term_id = report.term_id
        self.event_id = report.event_id
        self.payment_id = report.payment_id
        self.amount = report.amount
        self.type = report.type
        self.creation_date = report.creation_date
        return self.save()

    def save(self):
        self.payment_id = str(self.payment_id).rjust(20, '0')
        return BaseModel.save(self)
