# -*- coding: utf-8 -*-
"""
    Модель для таблицы связей кошелёк<->акция

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel

from helpers import date_helper


class WalletLoyalty(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'wallet_loyalty'

    STATUS_OFF = 0
    STATUS_CONNECTING = 1
    STATUS_ERROR = 2
    STATUS_ON = 3

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer)
    loyalty_id = db.Column(db.Integer)
    summ = db.Column(db.String(50))
    bonus_limit = db.Column(db.Integer)
    checked = db.Column(db.String(1024))
    status = db.Column(db.Integer)
    errors = db.Column(db.String(1024))

    @staticmethod
    def get_by_wallet_list(wallet_list, loyalty_id=False):
        query = WalletLoyalty.query
        query = query.filter(WalletLoyalty.wallet_id.in_(wallet_list))

        if loyalty_id:
            query = query.filter_by(loyalty_id=loyalty_id)
        return query.all()
