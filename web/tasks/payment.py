# -*- coding: utf-8 -*-
"""
    Задачи связанные с платежами

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import app
from web.celery import celery

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi

from helpers import date_helper

from models.payment_history import PaymentHistory
from models.payment_card import PaymentCard
from models.payment_wallet import PaymentWallet


class PaymentTask (object):

    # TODO добавить отлов потеряных операций
    @staticmethod
    @celery.task
    def background_payment(term_id, amount, payment_id):
        """Проводим фоновый платеж"""

        status = False
        wallet = PaymentWallet.query.filter_by(payment_id=payment_id).first()
        if not wallet:
            app.logger.error('Not found wallet with pid %s' % payment_id)

            return False

        history = PaymentHistory()
        history.type = PaymentHistory.TYPE_PAYMENT
        history.amount = amount
        history.user_id = wallet.user_id
        history.wallet_id = wallet.id
        history.term_id = term_id
        history.save()

        card = PaymentCard.query.filter_by(
            wallet_id=wallet.id,
            status=PaymentCard.STATUS_PAYMENT).first(
            )
        if not card:
            wallet.blacklist = PaymentWallet.ACTIVE_OFF
            wallet.save()
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        status = ym.background_payment(amount, card.token)
        if not status:
            app.logger.error(
                'Fail in background payment, wallet %s' %
                wallet.id)
            return False

        return status

    @staticmethod
    @celery.task
    def check_linking_manager():
        all_history = PaymentHistory.query.filter_by(
            type=PaymentHistory.TYPE_SYSTEM,
            status=PaymentHistory.STATUS_NEW).all()

        for key in all_history:
            PaymentTask.check_linking.delay(key)

        return True

    @staticmethod
    @celery.task
    def check_linking(history):
        history.status = PaymentHistory.STATUS_FAILURE
        history.save()

        result = PaymentCard().linking_card(history.request_id)
        if not result:
            delta = date_helper.get_curent_date(
                format=False) - history.creation_date

            if delta.total_seconds() > PaymentCard.MAX_LINKING_CARD_TIMEOUT:
                history.delete()
                return True

            history.status = PaymentHistory.STATUS_NEW
            history.save()

        return True
