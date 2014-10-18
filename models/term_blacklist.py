# -*- coding: utf-8 -*-
"""
    Модель для черного списка карта

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from helpers import date_helper

from models.base_model import BaseModel
from models.person import Person
from models.payment_wallet import PaymentWallet


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

    def __repr__(self):
        return '<payment_id %r>' % (self.payment_id)

    @staticmethod
    def get_max_timestamp():
        return db.session.query(
            db.func.max(TermBlacklist.timestamp)).scalar()

    @staticmethod
    def generate_blacklist():
        wallets = PaymentWallet.get_full()
        if not wallets:
            return False

        valid = set()
        blacklist = set()
        for wallet in wallets:
            if int(wallet.blacklist) == PaymentWallet.ACTIVE_OFF:
                blacklist.add(str(wallet.payment_id))
            elif int(wallet.status) != PaymentWallet.STATUS_ACTIVE:
                blacklist.add(str(wallet.payment_id))
            else:
                valid.add(str(wallet.payment_id))

        # Start: Костыль на время перехода от кошельков с балансом
        wallets_not_empty = PaymentWallet.get_not_empty()
        for wallet in wallets_not_empty:
            blacklist.discard(wallet.payment_id)

        wallets_empty = PaymentWallet.get_empty()
        for wallet in wallets_empty:
            if wallet.payment_id not in valid:
                blacklist.add(wallet.payment_id)
        # End

        persons = Person.query.group_by(Person.payment_id).all()
        for person in persons:
            if not person.payment_id:
                continue

            if person.payment_id not in valid:
                blacklist.add(person.payment_id)

        return set(list(blacklist))

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
