# -*- coding: utf-8 -*-
"""
    Модель для платежной карты (кошелька)


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.user import User
from web.helpers.date_helper import *


class PaymentWallet(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'wallet'

    STATUS_NOACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer(150), index=True)
    hard_id = db.Column(db.Integer(150), index=True)
    name = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    discodes_id = db.Column(db.Integer(), index=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self, id):
        self.discodes_id = 0
        self.balance = 0
        self.status = self.STATUS_NOACTIVE

    def __repr__(self):
        return '<id %r>' % (self.id)

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
