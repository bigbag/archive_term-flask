# -*- coding: utf-8 -*-
"""
Модель платежная карта

"""
from api import db
from api.helpers.date_helper import *


class Wallet(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'wallet'

    STATUS_NOACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer(150), index=True)
    name = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer(), index=True)
    discodes_id = db.Column(db.Integer(), index=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    balance = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<id %r>' % (self.id)

    def save(self):
        if not self.creation_date:
            self.creation_date = get_curent_date()
        db.session.commit()
