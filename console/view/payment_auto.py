# -*- coding: utf-8 -*-
"""
    Консольное приложение для проведения автоплатежей

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
from flask.ext.script import Command

from console import app
from configs.uniteller import UnitellerConfig
from libs.uniteller_api import UnitellerApi

from helpers import date_helper

from models.payment_wallet import PaymentWallet
from models.payment_history import PaymentHistory
from models.payment_reccurent import PaymentReccurent


class PaymentAuto(Command):

    "Run auto payment"

    def run_reccurents(self):
        reccurents = PaymentReccurent.query.filter_by(
            status=PaymentReccurent.STATUS_ON).all()

        un = UnitellerApi(UnitellerConfig)

        for reccurent in reccurents:
            print reccurent
            amount = 0
            reccurent.count = reccurent.count + 1

            if not reccurent.wallet:
                continue

            """ Делается одна попытка пополнить кошелек.
                Если она не успешна, скрипт делается попытки на кратном PERIOD_LENGH проходе.
                Если за MAX_PERIOD*PERIOD_LENGH проходов пополнение не удалось
                больше попыток не делается"""

            count = int(reccurent.count)
            current_period = count // PaymentReccurent.PERIOD_LENGH

            if current_period > PaymentReccurent.MAX_PERIOD:
                continue

            delta = count % PaymentReccurent.PERIOD_LENGH
            if not delta == 0:
                reccurent.status = PaymentReccurent.STATUS_OFF
                reccurent.save()
                continue

            amount = int(reccurent.amount) - int(reccurent.wallet.balance)

            history = PaymentHistory()
            history.user_id = reccurent.wallet.user_id
            history.wallet_id = reccurent.wallet_id
            history.amount = amount
            history.type = PaymentHistory.TYPE_PLUS

            if not history.save():
                continue

            order = dict(
                order_id=history.id,
                amount=amount / 100,
                parent_order_id=reccurent.history_id,
            )

            result = un.reccurent_payment(order)
            if result == UnitellerApi.STATUS_COMPLETE:
                reccurent.history_id = history.id
                reccurent.count = 0

            reccurent.status = PaymentReccurent.STATUS_OFF
            reccurent.run_date = date_helper.get_curent_date()
            reccurent.save()

    def run(self):
        try:
            self.run_reccurents()
        except Exception as e:
            app.logger.error(e)
