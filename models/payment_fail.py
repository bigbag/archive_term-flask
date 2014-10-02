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


class PaymentFail(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'fail'

    LOCK_FREE = 0
    LOCK_SET = 1

    report_id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False, index=True)
    timestamp = db.Column(db.Integer, nullable=False)
    lock = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self, report_id):
        self.count = 0
        self.lock = self.LOCK_FREE
        self.report_id = report_id

    def __repr__(self):
        return '<report_id %r>' % (self.report_id)

    @staticmethod
    def add_or_update(report_id):
        payment = PaymentFail.query.get(report_id)
        if not payment:
            payment = PaymentFail(report_id)
        return payment.save()

    def save(self):
        self.count += 1
        self.timestamp = date_helper.get_curent_utc()
        return BaseModel.save(self)
