# -*- coding: utf-8 -*-
"""
    Модель для привязанных карт


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import db

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi

from models.base_model import BaseModel
from models.payment_history import PaymentHistory
from models.payment_wallet import PaymentWallet
from models.user import User


class PaymentCard(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'payment_card'

    STATUS_PAYMENT = 1
    STATUS_ARCHIV = 0

    TYPE_VISA = 1
    TYPE_MC = 2

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    pan = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    type = db.Column(db.Integer(), nullable=False, index=True)
    status = db.Column(db.Integer(), nullable=False, index=True)

    def linking_card_init(self, discodes_id):
        """Инициализируем привязку карты"""

        wallet = PaymentWallet.query.filter(
            PaymentWallet.discodes_id == discodes_id).filter(
                PaymentWallet.user_id != 0).first(
                )
        if not wallet:
            return False

        history = PaymentHistory()
        history.type = PaymentHistory.TYPE_SYSTEM
        history.amount = PaymentHistory.SYSTEM_PAYMENT
        history.user_id = wallet.user_id
        history.wallet_id = wallet.id

        if not history.save():
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        status = ym.get_linking_card_params(history.id)
        if status:
            history.request_id = status['params']['cps_context_id']
            if not history.save():
                return False

            old_history = PaymentHistory().query.filter(PaymentHistory.id != history.id).filter(
                PaymentHistory.wallet_id == history.wallet_id).filter(
                    PaymentHistory.type == PaymentHistory.TYPE_SYSTEM).filter(
                        PaymentHistory.status == PaymentHistory.STATUS_NEW).all()

            for row in old_history:
                db.session.delete(row)
            db.session.commit()
        return status
