# -*- coding: utf-8 -*-
"""
    Модель для истории пополнений


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app
from models.payment_wallet import PaymentWallet
from models.payment_history import PaymentHistory
from helpers import date_helper


class PaymentLog(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('history.id'), index=True)
    history = db.relationship('PaymentHistory')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    rrn = db.Column(db.String(32), nullable=False)
    card_pan = db.Column(db.String(32), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.creation_date = date_helper.get_curent_date()

    def __repr__(self):
        return '<id %r>' % (self.history_id)

    def get_by_history_id(self, history_id):
        return self.query.filter_by(history_id=history_id).first()

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
