# -*- coding: utf-8 -*-
"""
    Модель для потерянных операций

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib

from web import db

from helpers import date_helper
from models.base_model import BaseModel


class PaymentLost(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'fail'

    report_id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, index=True)
    create_timestamp = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.count = 0

    def save(self):
        self.create_timestamp = date_helper.get_curent_utc
        return BaseModel.save(self)
