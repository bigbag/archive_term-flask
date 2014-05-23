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

from configs.uniteller import UnitellerConfig
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
        pass
