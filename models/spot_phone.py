# -*- coding: utf-8 -*-
"""
    Модель для привязанных к споту телефонных номеров

    :copyright: (c) 2015 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class SpotPhone(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot_phone'

    SERVICE_DISABLED = 0
    SERVICE_ENABLED = 1

    id = db.Column(db.Integer, primary_key=True)
    discodes_id = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(64), nullable=False)
    school_sms = db.Column(db.Integer)
