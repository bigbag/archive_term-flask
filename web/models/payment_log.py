# -*- coding: utf-8 -*-
"""
    Модель для истории пополнений


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.payment_wallet import PaymentWallet
from web.models.payment_history import PaymentHistory
from web.helpers.date_helper import *


class PaymentLog(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'log'

    history_id = db.Column(
        db.Integer,
        db.ForeignKey('history.id'),
        primary_key=True)
    history = db.relationship('PaymentHistory')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    wallet = db.relationship('PaymentWallet')
    rrn = db.Column(db.String(32), nullable=False)
    card_pan = db.Column(db.String(32), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<id %r>' % (self.history_id)

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
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            return False
        else:
            return True
