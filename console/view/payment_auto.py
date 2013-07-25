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

from web.helpers.date_helper import *

from web.models.payment_wallet import PaymentWallet
from web.models.payment_history import PaymentHistory
from web.models.payment_reccurent import PaymentReccurent


class PaymentAuto(Command):

    "Run auto payment"

    def run_recurrents(self):
        recurrents = PaymentReccurent.query.filter_by(
            status=PaymentReccurent.STATUS_ON).all()

        un = UnitellerApi(UnitellerConfig)

        for recurrent in recurrents:

            if not reccurent.wallet:
                continue

            amount = 0

            if recurrent.type == PaymentReccurent.TYPE_CEILING:
                amount = int(recurrent.amount) - int(reccurent.wallet.balance)

            elif recurrent.type == PaymentReccurent.TYPE_LIMIT:
                i = 1
                limit = PaymentReccurent.PAYMENT_MIN + \
                    PaymentReccurent.BALANCE_MIN
                while int(reccurent.wallet.balance) + amount <= limit:
                    amount = int(recurrent.amount) * i
                    i = i + 1
            else:
                continue

            if amount < PaymentReccurent.PAYMENT_MIN:
                continue

            history = PaymentHistory()
            history.user_id = reccurent.wallet.user_id
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

            if result == UnitellerApi.STATUS_COMPLETE:
                recurrent.history_id = history.id

            recurrent.status = PaymentReccurent.STATUS_OFF
            recurrent.run_date = get_curent_date()
            recurrent.save()

    def run(self):
        try:
            self.run_recurrents()
        except Exception as e:
            app.logger.error(e)
