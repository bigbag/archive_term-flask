# -*- coding: utf-8 -*-
"""
    Модель для операций без кошельков

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
from web import db
from web import app
from models.term import Term
from models.event import Event


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
    payment_id = db.Column(db.String(20))
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.amount = 0
        self.type = self.TYPE_WHITE

    def __repr__(self):
        return '<id %r>' % (self.id)

    def add_lost_payment(self, report):
        self.term_id = report.term_id
        self.event_id = report.event_id
        self.payment_id = report.payment_id
        self.amount = report.amount
        self.type = report.type
        self.creation_date = report.creation_date
        return self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            self.payment_id = str(self.payment_id).rjust(20, '0')
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
