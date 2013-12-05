# -*- coding: utf-8 -*-
"""
    Консольное приложение для тестирования и отладки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import random
import csv
import uuid
import urllib
from flask.ext.script import Command
from models.person import Person
from models.payment_wallet import PaymentWallet
from models.payment_history import PaymentHistory
from models.report import Report
from models.person_event import PersonEvent
from models.spot import Spot
from models.spot_dis import SpotDis

from console.configs.payment import UnitellerConfig
from console.configs.smsru import SmsruConfig
from libs.uniteller_api import UnitellerApi
from libs.smsru_api import SmsruApi

from helpers import hash_helper


class TestCommand(Command):

    def rate(self, count, all):
        random.seed()
        data = range(1, all + 1)
        random.shuffle(data)
        rate = sorted(random.sample(data, count))

        return rate

    def importCsv(self, file):
        spamreader = False
        with open(file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                print ', '.join(row)

        return spamreader

    def correct_balans_by_report(self):
        wallets = PaymentWallet.query.filter(
            PaymentWallet.user_id != 0).all()

        for wallet in wallets:
            history = PaymentHistory.query.filter_by(
                wallet_id=wallet.id,
                type=1,
                status=1,
            ).all()

            summ_plus = 0
            for row in history:
                summ_plus = summ_plus + int(row.amount)

            reports = Report.query.filter(
                Report.payment_id == wallet.payment_id).all()

            summ_minus = 0
            for report in reports:
                summ_minus = summ_minus + int(report.amount)

            wallet.balance = summ_plus - summ_minus
            wallet.save()

    def correct_balans_by_history(self):
        wallets = PaymentWallet.query.filter(
            PaymentWallet.user_id != 0).all()

        for wallet in wallets:
            plus = PaymentHistory.query.filter_by(
                wallet_id=wallet.id,
                type=1,
                status=1,
            ).all()

            summ_plus = 0
            for row in plus:
                summ_plus = summ_plus + int(row.amount)

            minus = PaymentHistory.query.filter_by(
                wallet_id=wallet.id,
                type=-1,
                status=1,
            ).all()

            summ_minus = 0
            for row in minus:
                summ_minus = summ_minus + int(row.amount)

            print wallet.id
            print wallet.balance
            wallet.balance = summ_plus - summ_minus
            wallet.save()

    def correct_history(self):
        reports = Report.query.order_by('id DESC').all()

        for report in reports:
            history = PaymentHistory.query.filter_by(
                creation_date=report.creation_date,
                term_id=report.term_id,
                amount=report.amount,
                type=-1
            ).first()

            if not history:
                continue

            try_wallet = PaymentWallet.query.filter_by(
                payment_id=report.payment_id).first()

            if not try_wallet.id == history.wallet_id:

                false_wallet = PaymentWallet.query.get(history.wallet_id)

                history.user_id = try_wallet.user_id
                history.wallet_id = try_wallet.id
                history.save()

                try_wallet.balance = int(
                    try_wallet.balance) - int(
                        history.amount)
                try_wallet.save()

                false_wallet.balance = int(
                    try_wallet.balance) + int(
                        history.amount)

                false_wallet.save()

    def get_person_balance_info(self, wallet_id):
        history = PaymentHistory.query.filter_by(
            wallet_id=wallet_id,
            status=1,
        ).all()

        balance = 0
        for row in history:
            balance = balance + row.type * int(row.amount)
            history_type = 'Plus'

            if row.type == PaymentHistory.TYPE_MINUS:
                history_type = 'Minus'

            date = row.creation_date.strftime('%H:%M:%S %d.%m.%Y')
            data = (
                date,
                str(int(row.amount) / 100),
                history_type,
                str(balance / 100),
            )

            print "%s,%s,%s,%s" % data

    def import_wallet(self):
        with open('tmp/import.csv', 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in spamreader:
                spot = Spot.query.filter(Spot.code == row[2]).first()

                if not spot:
                    continue

                wallet = PaymentWallet().filter(
                    PaymentWallet.discodes_id == spot.discodes_id).first()

                if wallet:
                    continue

                wallet = PaymentWallet()
                wallet.hard_id = row[0]
                wallet.payment_id = row[1]
                wallet.discodes_id = spot.discodes_id
                wallet.save()

    def run(self):
        sms = SmsruApi(SmsruConfig)
        to = '79627056382'
        text = 'Test'
        print sms.sms_send(to, text).response.body
