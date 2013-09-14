# -*- coding: utf-8 -*-
"""
    Консольное приложение для получения информации об операциях с ПС

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
from datetime import datetime
from datetime import timedelta

from flask.ext.script import Command
from console import app
from console.configs.payment import UnitellerConfig

from libs.uniteller_api import UnitellerApi
from models.payment_history import PaymentHistory
from models.payment_log import PaymentLog
from models.payment_wallet import PaymentWallet


class PaymentInfo(Command):

    "Return payment info"

    def set_new_payment(self):
        date_start = datetime.utcnow() - timedelta(days=1)
        date_stop = datetime.utcnow() - timedelta(minutes=1)

        payment_history = PaymentHistory.query.filter(
            (PaymentHistory.type == PaymentHistory.TYPE_PLUS) &
            (PaymentHistory.status == PaymentHistory.STATUS_NEW) &
            (PaymentHistory.creation_date >= date_start) &
            (PaymentHistory.creation_date < date_stop)
        ).all()

        un = UnitellerApi(UnitellerConfig)
        un.success = UnitellerApi.SUCCESS_ALL
        info = un.get_payment_info()

        if not info:
            return

        for history in payment_history:
            if not str(history.id) in info:
                continue

            payment_info = info[str(history.id)]

            if payment_info['status'] == UnitellerApi.STATUS_COMPLETE or payment_info['status'] == UnitellerApi.STATUS_AUTH:
                history.status = PaymentHistory.STATUS_COMPLETE
                if not history.save():
                    continue

                log = PaymentLog().get_by_history_id(history.id)
                if log:
                    continue

                log = PaymentLog()
                log.history_id = history.id
                log.creation_date = history.creation_date
                log.wallet_id = history.wallet_id
                log.rrn = payment_info['billnumber']
                log.card_pan = payment_info['cardnumber']
                log.save()

                wallet = PaymentWallet.query.get(history.wallet_id)
                wallet.balance = int(wallet.balance) + int(history.amount)
                wallet.save()
            else:
                history.status = PaymentHistory.STATUS_FAILURE
                history.save()

    def set_missing_payment(self):
        date_start = datetime.utcnow() - timedelta(days=1)
        date_stop = datetime.utcnow() - timedelta(minutes=15)

        payment_history = PaymentHistory.query.filter(
            (PaymentHistory.type == PaymentHistory.TYPE_PLUS) &
            (PaymentHistory.creation_date >= date_start) &
            (PaymentHistory.creation_date < date_stop)
        ).all()

        un = UnitellerApi(UnitellerConfig)
        un.success = UnitellerApi.SUCCESS_ALL
        info = un.get_payment_info()

        if not info:
            return

        for history in payment_history:
            if not str(history.id) in info:
                if history.status == PaymentHistory.STATUS_NEW:
                    history.status = PaymentHistory.STATUS_MISSING
                    history.save()

            else:
                payment_info = info[str(history.id)]
                if history.status == PaymentHistory.STATUS_FAILURE:
                    if payment_info['status'] == UnitellerApi.STATUS_COMPLETE:

                        wallet = PaymentWallet.query.get(history.wallet_id)
                        wallet.balance = int(
                            wallet.balance) + int(
                                history.amount)

                        if not wallet.save():
                            continue

                        history.status = PaymentHistory.STATUS_COMPLETE
                        history.save()
                elif history.status == PaymentHistory.STATUS_COMPLETE:
                    if payment_info['status'] == UnitellerApi.STATUS_CANCELED:

                        wallet = PaymentWallet.query.get(history.wallet_id)
                        wallet.balance = int(
                            wallet.balance) - int(
                                history.amount)

                        if not wallet.save():
                            continue

                        history.status = PaymentHistory.STATUS_FAILURE
                        history.save()

    def run(self):
        try:
            self.set_new_payment()
            self.set_missing_payment()
        except Exception as e:
            app.logger.error(e)
