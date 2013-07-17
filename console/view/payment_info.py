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
from console import db
from console.configs.payment import UnitellerConfig
from libs.uniteller_api import UnitellerApi
from web.models.payment_history import PaymentHistory
from web.models.payment_log import PaymentLog
from web.models.payment_wallet import PaymentWallet


class PaymentInfo(Command):

    "Return payment info"

    def set_info(self):
        date_start = datetime.utcnow() - timedelta(days=2)
        date_stop = datetime.utcnow() - timedelta(minutes=10)

        payment_history = PaymentHistory.query.filter(
            (PaymentHistory.type == PaymentHistory.TYPE_PLUS) &
            (PaymentHistory.status != PaymentHistory.STATUS_FAILURE) &
            (PaymentHistory.creation_date >= date_start) &
            (PaymentHistory.creation_date < date_stop)
        ).limit(100).all()

        un = UnitellerApi(UnitellerConfig)

        for history in payment_history:
            log = PaymentLog.query.get(history.id)

            if log:
                continue

            info = un.get_payment_info(history.id)

            if history.status == PaymentHistory.STATUS_COMPLETE:
                if info['response_code'] == UnitellerApi.STATUS_COMPLETE:
                    log = PaymentLog()
                    log.history_id = history.id
                    log.wallet_id = history.wallet_id
                    log.rrn = info['billnumber']
                    log.card_pan = info['cardnumber']
                    log.save()

            elif history.status == PaymentHistory.STATUS_NEW:
                if info and info['response_code'] == UnitellerApi.STATUS_COMPLETE:
                    wallet = PaymentWallet.query.get(history.wallet_id)
                    wallet.balance = int(wallet.balance) + int(history.amount)
                    if not wallet.save():
                        continue
                    history.status = PaymentHistory.STATUS_COMPLETE
                    history.save()
                else:
                    history.status = PaymentHistory.STATUS_FAILURE
                    history.save()

    def run(self):
        while True:
            try:
                self.set_info()
            except Exception as e:
                app.logger.error(e)

            db.session.commit()
            db.session.close()
            time.sleep(5)
