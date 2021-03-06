# -*- coding: utf-8 -*-
"""
    Модель для привязанных карт


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import logging
from web import db

from yandex_money.api import Wallet, ExternalPayment

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

    LINKING_AMOUNT = 1

    TYPE_YM = 'Yandex'
    TYPE_MC = 'MasterCard'
    TYPE_VISA = 'VISA'

    PAYMENT_BY_CARD = 'AC'
    PAYMENT_BY_YM = 'PC'

    SYSTEM_MPS = 0
    SYSTEM_YANDEX = 1

    MAX_LINKING_CARD_TIMEOUT = 60 * 60

    log = logging.getLogger('payment')

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    pan = db.Column(db.String(128), nullable=True)
    token = db.Column(db.Text(), nullable=False)
    type = db.Column(db.String(128), nullable=False, index=True)
    system = db.Column(db.Integer(), nullable=False, index=True)
    status = db.Column(db.Integer(), nullable=False, index=True)

    def __init__(self):
        self.system = self.SYSTEM_MPS
        self.status = self.STATUS_ARCHIV

    @staticmethod
    def get_payment_card(wallet_id):
        return PaymentCard.query.filter_by(
            wallet_id=wallet_id,
            status=PaymentCard.STATUS_PAYMENT).first()

    def get_ym_params(self, amount, pattern, order_id, success_uri, fail_uri, type=PAYMENT_BY_CARD):
        """Запрос параметров от ym"""

        request_options = {
            "pattern_id": pattern,
            "sum": amount,
            "customerNumber": order_id,
        }

        if type == PaymentCard.PAYMENT_BY_CARD:
            ym = ExternalPayment(YandexMoneyConfig.INSTANCE_ID)
            payment = ym.request(request_options)
        elif type == PaymentCard.PAYMENT_BY_YM:
            return False
        else:
            return False

        if payment['status'] == "success":
            request_id = payment['request_id']
        else:
            return False

        process_options = {
            "request_id": request_id,
            'ext_auth_success_uri': success_uri,
            'ext_auth_fail_uri': fail_uri
        }
        result = ym.process(process_options)

        return dict(
            url=result['acs_uri'],
            params=result['acs_params']
        )

    def get_linking_params(self, order_id=0, url=None):
        """Запрос параметров для привязки карты"""

        ym = YaMoneyApi(YandexMoneyConfig)
        return self.get_ym_params(self.LINKING_AMOUNT,
                                  ym.const.CARD_PATTERN_ID,
                                  order_id,
                                  url,
                                  url,
                                  self.PAYMENT_BY_CARD)

    def linking_init(self, discodes_id, url=None):
        """Инициализируем привязку карты"""

        wallet = PaymentWallet.get_valid_by_discodes_id(discodes_id)
        if not wallet:
            return False

        history = PaymentHistory()
        history.add_linking_record(wallet.user_id, wallet.id)
        if not history.save():
            return False

        status = self.get_linking_params(history.id, url)
        if not status:
            history.delete()
            self.log.error('Linking card: Fail in getting parameters')
            return False

        history.request_id = status['params']['cps_context_id']
        if not history.save():
            return False

        fail_history = PaymentHistory.get_fail_linking_record(
            history.id, history.wallet_id)
        for row in fail_history:
            db.session.delete(row)
        db.session.commit()

        return status

    def linking_card(self, history_id):
        """Привязываем карту, получаем платежный токен"""

        from web.tasks.payment import PaymentTask

        history = PaymentHistory.query.get(history_id)
        if not history:
            return False

        if history.status == PaymentHistory.STATUS_COMPLETE:
            return False

        wallet = PaymentWallet.query.get(history.wallet_id)
        if not wallet:
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        result = ym.get_process_external_payment(history.request_id)
        if not result or not 'status' in result:
            message = 'Linking card: Not found status field, request_id=%s' % history.request_id
            self.log.error(message)
            return message

        if result['status'] == 'in_progress':
            history.status = PaymentHistory.STATUS_IN_PROGRESS
            if not history.save():
                return False
            return result
        elif result['status'] == 'refused':
            history.status = PaymentHistory.STATUS_FAILURE
            if not history.save():
                return False
            return result

        if result['status'] != 'success':
            return result

        PaymentCard.set_archiv(history.wallet_id)

        card = self.add_payment(history, result)
        if not card:
            return False

        history.invoice_id = result['invoice_id']
        history.status = PaymentHistory.STATUS_COMPLETE
        if not history.save():
            return False

        if not card.save():
            return False

        PaymentTask.restart_fail_algorithm.delay(history.wallet_id)

        wallet.blacklist = PaymentWallet.ACTIVE_ON
        wallet.save()

        return result

    @staticmethod
    def set_archiv(wallet_id):
        """Переводим все карты привязанные к кошельку в архивное состояние"""

        old_cards = PaymentCard.query.filter_by(
            wallet_id=wallet_id,
            status=PaymentCard.STATUS_PAYMENT).all()

        for row in old_cards:
            row.status = PaymentCard.STATUS_ARCHIV
            db.session.add(row)
        db.session.commit()

        return True

    def add_payment(self, history, status):
        """ Добавляем платежную карту"""

        card = PaymentCard()
        card.user_id = history.user_id
        card.wallet_id = history.wallet_id

        if not 'money_source' in status:
            self.log.error('Linking card: Not found card parameters')
            return False
        if not 'pan_fragment' in status['money_source'] or not 'payment_card_type' in status['money_source']:
            self.log.error('Linking card: Not found card parameters')
            return False

        card.token = status['money_source']['money_source_token']
        card.pan = status['money_source']['pan_fragment']
        card.type = status['money_source']['payment_card_type']
        card.status = PaymentCard.STATUS_PAYMENT

        return card

    @staticmethod
    def add_ym_wallet(wallet, token):
        """ Добавляем кошелек яндекс"""

        card = PaymentCard()
        card.user_id = wallet.user_id
        card.wallet_id = wallet.id
        card.token = token
        card.type = PaymentCard.TYPE_YM
        card.system = PaymentCard.SYSTEM_YANDEX
        card.status = PaymentCard.STATUS_PAYMENT

        return card
