# -*- coding: utf-8 -*-
"""
    Модель для истории операций по кошельку


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.term import Term
from web.models.user import User
from web.helpers.date_helper import *


class PaymentHistory(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'history'

    STATUS_NEW = 0
    STATUS_COMPLETE = 1
    STATUS_FAILURE = -1

    TYPE_MINUS = -1
    TYPE_PLUS = 1

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    wallet = db.relationship('PaymentWallet')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    amount = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.Integer(), nullable=False)

    def __init__(self):
        self.status = self.STATUS_NEW

    def __repr__(self):
        return '<id %r>' % (self.id)

    def add_history(self, wallet, report):
        self.user_id = wallet.user_id
        self.wallet_id = wallet.id
        self.term_id = report.term_id
        self.amount = report.amount
        self.type = PaymentHistory.TYPE_MINUS
        self.status = PaymentHistory.STATUS_COMPLETE
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        if not self.creation_date:
            self.creation_date = get_curent_date()
        db.session.add(self)
        db.session.commit()
