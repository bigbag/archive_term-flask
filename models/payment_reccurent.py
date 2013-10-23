# -*- coding: utf-8 -*-
"""
    Модель для таблицы автоплатежей


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app
from models.payment_wallet import PaymentWallet
from models.payment_history import PaymentHistory
from helpers import date_helper


class PaymentReccurent(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'reccurent'

    BALANCE_MIN = 4000
    PAYMENT_MIN = 10000

    STATUS_ON = 1
    STATUS_OFF = 0

    TYPE_CEILING = 0
    TYPE_LIMIT = 1

    MAX_COUNT = 3
    PERIOD = 20

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    history_id = db.Column(db.Integer, db.ForeignKey('history.id'), index=True)
    history = db.relationship('PaymentHistory')
    card_pan = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    run_date = db.Column(db.DateTime)
    type = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer)

    def __init__(self):
        self.creation_date = date_helper.get_curent_date()
        self.type = self.TYPE_CEILING
        self.status = self.STATUS_OFF
        self.count = 0

    def __repr__(self):
        return '<id %r>' % (self.wallet_id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
