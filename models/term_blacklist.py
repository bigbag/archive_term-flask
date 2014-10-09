# -*- coding: utf-8 -*-
"""
    Модель для черного списка карта

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from helpers import date_helper

from models.base_model import BaseModel


class TermBlacklist(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'blacklist'

    STATUS_PAYMENT = 0
    STATUS_BLACK = 1

    payment_id = db.Column(db.String(), primary_key=True)
    timestamp = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.Integer(), nullable=False, index=True)

    def __init__(self):
        self.status = self.STATUS_BLACK

    @staticmethod
    def get_all_list():
        all_cards = TermBlacklist.query.all()
        return set([str(row.payment_id) for row in all_cards])

    @staticmethod
    def get_all_black_list():
        all_cards = TermBlacklist.query.filter_by(
            status=TermBlacklist.STATUS_BLACK).all()
        return set([str(row.payment_id) for row in all_cards])

    def save(self):
        self.timestamp = date_helper.get_curent_utc()
        return BaseModel.save(self)
