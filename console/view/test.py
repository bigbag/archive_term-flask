# -*- coding: utf-8 -*-
"""
    Консольное приложение для тестирования и отладки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import random
import csv
import urllib

from flask.ext.script import Command

from web import db

from models.person import Person
from models.payment_wallet import PaymentWallet
from models.payment_lost import PaymentLost
from models.payment_history import PaymentHistory
from models.report import Report
from models.person_event import PersonEvent
from models.term import Term
from models.term_event import TermEvent
from models.firm_term import FirmTerm
from models.spot import Spot
from models.spot_dis import SpotDis
from models.report_stack import ReportStack

from web.tasks import report as ReportTask

from console.configs.payment import UnitellerConfig
from libs.uniteller_api import UnitellerApi


from helpers import hash_helper, date_helper


class TestCommand(Command):

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
        from models.spot import Spot
        from models.spot_dis import SpotDis
        from sqlalchemy.sql import func

        print Spot().get_max_code128()

        # from models.report import Report
        # from models.person import Person
        # from models.term import Term
        # from models.term_corp_wallet import TermCorpWallet

        # from datetime import datetime, timedelta
        # from sqlalchemy.sql import func

        # report_stack = ReportStack.query.get(53)
        # interval_meta = ReportStack().get_interval_meta(report_stack.interval)
        # type_meta = ReportStack().get_type_meta(report_stack.type)

        # persons = Person().get_dict_by_firm_id(report_stack.firm_id)
        # terms = Term().select_name_dict()
        # corp_wallets = TermCorpWallet().get_dict_by_firm_id(
        #     report_stack.firm_id)

        # if type_meta != 'person':
        #     return False

        # yesterday = datetime.now() - timedelta(2)
        # interval = date_helper.get_date_interval(yesterday, interval_meta)

        # query = db.session.query(
        #     Report.person_id,
        #     func.sum(Report.amount),
        #     Report.term_id,)

        # query = query.filter(Report.corp_type == Report.CORP_TYPE_ON)
        # query = query.filter(Report.person_firm_id == report_stack.firm_id)
        # query = query.filter(
        #     Report.creation_date.between(interval[0], interval[1]))

        # query = query.group_by(Report.person_id, Report.term_id)
        # query = query.order_by(Report.person_id)
        # reports = query.all()

        # result = {}
        # result['person'] = {}
        # for row in reports:
        #     if row[0] not in result['person']:
        #         result['person'][row[0]] = {}
        #         result['person'][row[0]]['amount'] = 0

        #     data = result['person'][row[0]]
        #     data['name'] = persons[row[0]]['name']
        #     data['tabel_id'] = persons[row[0]]['tabel_id']
        #     data['card'] = persons[row[0]]['card']

        #     if row[0] in corp_wallets:
        #         corp_wallet = corp_wallets[row[0]]
        #         data['wallet_interval'] = corp_wallet['interval']
        #         data['wallet_limit'] = corp_wallet['limit'] / 100
        #     data['amount'] = data['amount'] + row[1] / 100

        #     if 'term' not in data:
        #         data['term'] = {}
        #     term_name = terms[row[2]]
        #     data['term'][term_name] = row[1] / 100

        #     result['person'][row[0]] = data

        # print result

        # method = "report_%s_%s" % (interval_meta, type_meta)
        # print getattr(ReportTask, method)(report_stack)
