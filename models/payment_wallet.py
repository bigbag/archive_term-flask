# -*- coding: utf-8 -*-
"""
    Модель для платежной карты (кошелька)


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import random

from web import db
from web import app
from models.user import User

from helpers.date_helper import *
from helpers.hash_helper import *


class PaymentWallet(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'wallet'

    STATUS_NOACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), index=True)
    hard_id = db.Column(db.Integer(150), index=True)
    name = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    discodes_id = db.Column(db.Integer(), index=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.discodes_id = 0
        self.balance = 0
        self.creation_date = get_curent_date()
        self.status = self.STATUS_NOACTIVE

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_pid(self, pids):
        pid = "%s%s" % (pids, random.randint(100000000, 999999999))
        pid = "%s%s" % (pid, get_isin_checksum(pid))

        wallet = self.query.filter_by(payment_id=pid).first()
        if wallet:
            self.get_pid(self, pids)
        else:
            return pid

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
