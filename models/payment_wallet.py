# -*- coding: utf-8 -*-
"""
    Модель для платежной карты (кошелька)


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import random

from web import db

from models.base_model import BaseModel
from models.user import User

from helpers import date_helper, hash_helper


class PaymentWallet(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'wallet'

    STATUS_NOACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    ACTIVE_ON = 1
    ACTIVE_OFF = 0

    TYPE_DEMO = 0
    TYPE_FULL = 1

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), index=True)
    hard_id = db.Column(db.String(128), index=True)
    name = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    discodes_id = db.Column(db.Integer(), index=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    blacklist = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer(), index=True)

    def __init__(self):
        self.discodes_id = 0
        self.name = 'My spot'
        self.type = self.TYPE_FULL
        self.blacklist = self.ACTIVE_OFF
        self.user_id = 0
        self.creation_date = date_helper.get_curent_date()
        self.status = self.STATUS_NOACTIVE

    def add_to_blacklist(self):
        self.blacklist = PaymentWallet.ACTIVE_OFF
        if self.save():
            return self
        return False

    def remove_from_blacklist(self):
        self.blacklist = PaymentWallet.ACTIVE_ON
        if self.save():
            return self
        return False

    def get_pid(self, pids):
        pid = "%s%s" % (pids, random.randint(100000000, 999999999))
        pid = "%s%s" % (pid, hash_helper.get_isin_checksum(pid))
        pid = str(pid).rjust(20, '0')[-20:]

        wallet = self.query.filter_by(payment_id=pid).first()
        if wallet:
            self.get_pid(self, pids)
        else:
            return pid

    def get_by_payment_id(self, payment_id):
        return self.query.filter_by(payment_id=payment_id).first()

    def save(self):
        self.payment_id = str(self.payment_id).rjust(20, '0')
        return BaseModel.save(self)
