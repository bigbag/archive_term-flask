# -*- coding: utf-8 -*-
"""
    Консольное приложение для проведения автоплатежей

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
from flask.ext.script import Command

from console import app
from console.configs.payment import UnitellerConfig
from libs.uniteller_api import UnitellerApi

from web.models.payment_wallet import PaymentWallet
from web.models.payment_history import PaymentHistory
from web.models.payment_auto import PaymentAuto


class PaymentRecurrent(Command):

    "Run auto payment"

    def set_recurrents(self):
        recurrents = PaymentAuto.query.filter_by(
            status=PaymentAuto.STATUS_ON).all()

        un = UnitellerApi(UnitellerConfig)

        for recurrent in recurrents:

            wallet = PaymentWallet.query.get(recurrent.wallet_id)
            amount = 0

            if not wallet:
                continue

            if recurrent.type == PaymentAuto.TYPE_CEILING:
                amount = int(recurrent.amount) - int(wallet.balance)

            elif recurrent.type == PaymentAuto.TYPE_LIMIT:
                i = 1
                while int(wallet.balance) + amount < 11000:
                    amount = int(recurrent.amount) * i
                    i = i + 1
            else:
                continue

            if amount < 1:
                continue

            history = PaymentHistory()
            history.user_id = wallet.user_id
            history.wallet_id = recurrent.wallet_id
            history.amount = amount
            history.type = PaymentHistory.TYPE_PLUS

            if not history.save():
                continue

            order = dict(
                order_id=history.id,
                amount=amount / 100,
                parent_order_id=recurrent.history_id,
            )

            # result = un.recurrent_payment(order)

            # if result != UnitellerApi.STATUS_COMPLETE:
            #     continue

            wallet.balance = int(wallet.balance) + amount
            if (wallet.save()):
                history.status = PaymentHistory.STATUS_COMPLETE
                history.save()

                recurrent.status = PaymentAuto.STATUS_OFF
                recurrent.history_id = history.id
                recurrent.save()

    def run(self):
        recurrents = PaymentAuto.query.filter_by(
            status=PaymentAuto.STATUS_ON).all()

        un = UnitellerApi(UnitellerConfig)

        for recurrent in recurrents:

            wallet = PaymentWallet.query.get(recurrent.wallet_id)
            amount = 0

            if not wallet:
                continue

            if recurrent.type == PaymentAuto.TYPE_CEILING:
                amount = int(recurrent.amount) - int(wallet.balance)

            elif recurrent.type == PaymentAuto.TYPE_LIMIT:
                i = 1
                while int(wallet.balance) + amount < 11000:
                    amount = int(recurrent.amount) * i
                    i = i + 1
            else:
                continue

            if amount < 1:
                continue

            history = PaymentHistory()
            history.user_id = wallet.user_id
            history.wallet_id = recurrent.wallet_id
            history.amount = amount
            history.type = PaymentHistory.TYPE_PLUS

            if not history.save():
                continue

            order = dict(
                order_id=history.id,
                amount=amount / 100,
                parent_order_id=recurrent.history_id,
            )

            result = un.recurrent_payment(order)

            recurrent.status = PaymentAuto.STATUS_OFF
            recurrent.history_id = history.id
            recurrent.save()
