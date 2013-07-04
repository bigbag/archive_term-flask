# -*- coding: utf-8 -*-
"""
    Модель для операций без кошельков

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import time
from web import db
from web.models.term import Term
from web.models.event import Event
from web.helpers.date_helper import *


class PaymentLost(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'lost'

    TYPE_WHITE = 0
    TYPE_PAYMENT = 1

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    payment_id = db.Column(db.String(150))
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    check_summ = db.Column(db.String(32), nullable=False)

    def __init__(self):
        self.amount = 0
        self.type = self.TYPE_WHITE

    def __repr__(self):
        return '<id %r>' % (self.id)

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
        if not self.check_summ:
            self.check_summ = self.get_check_summ()
        db.session.add(self)
        db.session.commit()
