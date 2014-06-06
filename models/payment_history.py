# -*- coding: utf-8 -*-
"""
    Модель для истории операций по кошельку


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib

from web import db

from models.base_model import BaseModel
from models.term import Term
from models.payment_wallet import PaymentWallet
from models.user import User

from helpers import date_helper


class PaymentHistory(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'history'

    STATUS_NEW = 0
    STATUS_IN_PROGRESS = 1
    STATUS_COMPLETE = 2
    STATUS_FAILURE = -1

    TYPE_SYSTEM = 1
    TYPE_PAYMENT = 2

    SYSTEM_PAYMENT = 1

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    amount = db.Column(db.String(50), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    request_id = db.Column(db.Text(), nullable=False)
    invoice_id = db.Column(db.Text())
    type = db.Column(db.Integer(), nullable=False, index=True)
    status = db.Column(db.Integer(), nullable=False, index=True)

    def __init__(self):
        self.term_id = 0
        self.status = self.STATUS_NEW
        self.type = self.TYPE_PAYMENT
        self.request_id = 0
        self.report_id = 0
        self.invoice_id = 0
        self.creation_date = date_helper.get_curent_date()

    def from_report(self, report, wallet):
        history = PaymentHistory()
        history.type = PaymentHistory.TYPE_PAYMENT
        history.amount = report.amount
        history.user_id = wallet.user_id
        history.report_id = report.id
        history.wallet_id = wallet.id
        history.term_id = report.term_id
        history.creation_date = report.creation_date
        history.report_id = report.id

        if not history.save():
            return False

        return history

    def get_fail_linking_record(self, history_id, wallet_id):
        return PaymentHistory().query.filter(PaymentHistory.id != history_id).filter(
            PaymentHistory.wallet_id == wallet_id).filter(
                PaymentHistory.type == PaymentHistory.TYPE_SYSTEM).filter(
                    PaymentHistory.status == PaymentHistory.STATUS_NEW).all()

    def add_linking_record(self, user_id, wallet_id):
        self.type = PaymentHistory.TYPE_SYSTEM
        self.amount = PaymentHistory.SYSTEM_PAYMENT
        self.user_id = user_id
        self.wallet_id = wallet_id
        return self

    def add_history(self, wallet, report):
        self.user_id = wallet.user_id
        self.wallet_id = wallet.id
        self.term_id = report.term.id
        self.creation_date = report.creation_date
        self.amount = report.amount
        self.type = PaymentHistory.TYPE_PAYMENT
        self.status = PaymentHistory.STATUS_COMPLETE
        return self.save()

    def get_new_by_wallet_id(self, wallet_id):
        return self.query.filter_by(status=self.STATUS_NEW, wallet_id=wallet_id).first()

    def get_new_payment(self):
        return PaymentHistory.query.filter(
            PaymentHistory.report_id != 0).filter(
                PaymentHistory.status == PaymentHistory.STATUS_NEW).filter(
                    PaymentHistory.request_id != 0).all(
                    )
