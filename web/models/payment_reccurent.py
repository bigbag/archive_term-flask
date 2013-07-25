# -*- coding: utf-8 -*-
"""
    Модель для таблицы автоплатежей


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.payment_wallet import PaymentWallet
from web.models.payment_history import PaymentHistory
from web.helpers.date_helper import *


class PaymentReccurent(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'reccurent'

    BALANCE_MIN = 4000
    PAYMENT_MIN = 10000

    STATUS_ON = 1
    STATUS_OFF = 0

    TYPE_CEILING = 0
    TYPE_LIMIT = 1

    wallet_id = db.Column(
        db.Integer,
        db.ForeignKey('wallet.id'),
        primary_key=True)
    wallet = db.relationship('PaymentWallet')
    history_id = db.Column(
        db.Integer,
        db.ForeignKey('history.id'),
        primary_key=True)
    card_pan = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    run_date = db.Column(db.DateTime)
    type = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.type = self.TYPE_CEILING
        self.status = self.STATUS_OFF

    def __repr__(self):
        return '<id %r>' % (self.wallet_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            if not self.creation_date:
                self.creation_date = get_curent_date()
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            return False
        else:
            return True
