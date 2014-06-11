# -*- coding: utf-8 -*-
"""
    Модель для корпоративной карты (кошелька)


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel
from models.person import Person

from helpers import date_helper


class TermCorpWallet(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'corp_wallet'

    STATUS_DISABLED = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    INTERVAL_ONCE = 0
    INTERVAL_DAY = 1
    INTERVAL_WEEK = 2
    INTERVAL_MONTH = 3

    BALANCE_MIN = 40

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    creation_date = db.Column(db.DateTime, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    limit = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.Integer, nullable=False, index=True)

    def __init__(self):
        self.limit = 0
        self.balance = 0
        self.interval = self.INTERVAL_MONTH
        self.creation_date = date_helper.get_curent_date()
        self.status = self.STATUS_ACTIVE

    def get_interval_list(self):
        return [
            {'id': self.INTERVAL_ONCE, 'name': u"Разовый"},
            {'id': self.INTERVAL_DAY, 'name': u"Дневной"},
            {'id': self.INTERVAL_WEEK, 'name': u"Недельный"},
            {'id': self.INTERVAL_MONTH, 'name': u"Месячный"}
        ]

    def get_max_limit_dict(self):
        return {
            self.INTERVAL_ONCE: 9999,
            self.INTERVAL_DAY: 1000,
            self.INTERVAL_WEEK: 2500,
            self.INTERVAL_MONTH: 9999
        }

    @cache.cached(timeout=120, key_prefix='corp_wallet')
    def get_dict_by_firm_id(self, firm_id):
        corp_wallet_interval = self.get_interval_list()
        persons = Person().get_dict_by_firm_id(firm_id)

        result = {}
        for key in persons:
            wallet = self.query.filter_by(person_id=key).first()
            if not wallet:
                continue

            result[key] = dict(
                interval=corp_wallet_interval[
                    wallet.interval][
                        'name'],
                limit=wallet.limit,
                balance=wallet.balance
            )
        return result

    def to_json(self):
        corp_wallet_interval = self.get_interval_list()
        items = dict(
            id=self.id,
            person_id=self.person_id,
            balance=self.balance / 100,
            limit=self.limit / 100,
            interval=self.interval,
            interval_name=corp_wallet_interval[self.interval]['name'],
        )
        return items
