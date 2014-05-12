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

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer)
    loyalty_id = db.Column(db.Integer)
    summ = db.Column(db.String(50))
    count = db.Column(db.Integer)
    part_count = db.Column(db.Integer)
    bonus_limit = db.Column(db.Integer)
    checked = db.Column(db.Integer)