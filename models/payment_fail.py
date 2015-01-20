# -*- coding: utf-8 -*-
"""
    Модель для потерянных операций

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from configs.general import Config

from helpers import date_helper

from web.tasks import mail
from web.emails.term.blacklist_alarm import BlacklistAlarmMessage

from models.base_model import BaseModel
from models.report import Report
from models.payment_card import PaymentCard
from models.payment_wallet import PaymentWallet
from models.user import User
from models.spot import Spot
from models.user_profile import UserProfile


class PaymentFail(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'fail'

    LOCK_FREE = 0
    LOCK_SET = 1

    report_id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, nullable=True)
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
        if payment:
            return payment.save()

        payment = PaymentFail(report_id)

        report = Report.query.get(report_id)
        if report:
            report.status = Report.STATUS_FAIL
            report.save()

            wallet = PaymentWallet.query.filter_by(
                payment_id=report.payment_id).first()
            if wallet:
                payment.wallet_id = wallet.id

        return payment.save()

    @staticmethod
    def blacklist_alert(report_id):
        payment = PaymentFail.query.get(report_id)
        if payment.count != Config.BLACKLIST_ALARM_LIMIT:
            return False

        report = Report.query.get(report_id)

        wallet = PaymentWallet.get_by_payment_id(report.payment_id)
        spot = Spot.query.filter_by(
            discodes_id=wallet.discodes_id).first()
        card = PaymentCard.get_payment_card(wallet.id)
        user = User.query.get(wallet.user_id)

        if not spot or not user or not card:
            return False

        username = u'Dear user'
        if user.lang == 'ru':
            username = u'Уважаемый пользователь'

        user_profile = UserProfile.query.filter_by(
            user_id=user.id).first()

        if user_profile and user_profile.name:
            username = user_profile.name

        mail.send.delay(
            BlacklistAlarmMessage,
            to=user.email,
            lang=user.lang,
            username=username,
            spotname=spot.name,
            card_pan=u'%s %s' % (card.type, card.pan)
        )

        return True

    def save(self):
        self.count += 1
        self.timestamp = date_helper.get_current_utc()
        return BaseModel.save(self)
