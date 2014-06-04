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

    MAX_LINKING_CARD_TIMEOUT = 60 * 60

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    pan = db.Column(db.String(128), nullable=False)
    token = db.Column(db.Text(), nullable=False)
    type = db.Column(db.String(128), nullable=False, index=True)
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
        history.add_linking_record(wallet.user_id, wallet.id)
        if not history.save():
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        status = ym.get_linking_card_params(history.id)
        if not status:
            history.delete()
            return False

        history.request_id = status['params']['cps_context_id']
        if not history.save():
            return False

        fail_history = PaymentHistory().get_fail_linking_record(
            history.id, history.wallet_id)
        for row in fail_history:
            db.session.delete(row)
        db.session.commit()
        return status

    def linking_card(self, request_id):
        """Привязываем карту, получаем платежный токен"""

        history = PaymentHistory.query.filter_by(request_id=request_id).first()
        if not history:
            return False

        if history.status == PaymentHistory.STATUS_COMPLETE:
            return False

        wallet = PaymentWallet.query.get(history.wallet_id)
        if not wallet:
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        status = ym.get_payment_info(request_id)
        if not status:
            return False

        if status['status'] != 'success':
            return False

        history.invoice_id = status['invoice_id']
        history.status = PaymentHistory.STATUS_COMPLETE
        if not history.save():
            return False

        old_cards = PaymentCard.query.filter_by(
            wallet_id=history.wallet_id,
            status=PaymentCard.STATUS_PAYMENT).all()
        for row in old_cards:
            row.status = PaymentCard.STATUS_ARCHIV
            db.session.add(row)
        db.session.commit()

        card = PaymentCard()
        card.user_id = history.user_id
        card.wallet_id = history.wallet_id
        card.token = status['token']
        card.pan = status['card_pan']
        card.type = status['card_type']
        card.status = PaymentCard.STATUS_PAYMENT

        if not card.save():
            return False

        wallet.blacklist = PaymentWallet.ACTIVE_ON
        wallet.save()

        return status