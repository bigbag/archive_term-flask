# -*- coding: utf-8 -*-
"""
    Тест моделей платежки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest
import os
from web import db, app

from datetime import datetime

from models.payment_history import PaymentHistory
from models.payment_wallet import PaymentWallet
from models.report import Report
from models.payment_account import PaymentAccount

from helpers import date_helper


class ModelsPaymentCase(unittest.TestCase):

    USER_ID = 1
    WALLET_ID = 1
    TERM_ID = 21
    EVENT_ID = 99
    HARD_ID = '9995749700230784'
    PAYMENT_ID = '99999999999999999999'
    PIDS = '0077781000'
    DISCODES_ID = 999999
    HISTORY_ID = 100000000
    CARD_PAN = '4405050300000000'
    RRN = '999999999999'
    AMOUNT = 1000
    TEST_STRING = 'Test'
    TEST_TEXT = 'Test test test'
    TEST_EMAIL = 'test1@test.ru'
    TEST_DATE = '2013-08-27 00:00:01'
    TERM_ID = 21
    PERSON_ID = 1
    FIRM_ID = 8
    ACCOUNT_ID = 1
    ACCOUNT_STATUS = 0
    ACCOUNT_FILENAME = 'account_firm_8_date_08_2014.pdf'
    ITEMS_COUNT = 100

    def model_test(self, Model, data):
        old = Model()
        old.__dict__.update(data)

        assert old.save()
        new = Model.query.get(old.id)
        old.delete()
        assert not Model.query.get(new.id)

    def test_payment_history(self):
        data = dict(
            user_id=self.USER_ID,
            wallet_id=self.WALLET_ID,
            amount=self.AMOUNT,
            type=1
        )
        self.model_test(PaymentHistory, data)

    def test_func_add_history(self):
        history = PaymentHistory()

        data_wallet = dict(
            id=1,
            payment_id=self.PAYMENT_ID,
            hard_id=self.HARD_ID,
            name=self.TEST_STRING,
            user_id=self.USER_ID,
            discodes_id=self.DISCODES_ID,
            card_pan=self.CARD_PAN
        )
        wallet = PaymentWallet()
        wallet.__dict__.update(data_wallet)

        data_report = dict(
            term_id=self.TERM_ID,
            event_id=self.EVENT_ID,
            person_id=self.PERSON_ID,
            payment_id=self.FIRM_ID,
            firm_id=self.FIRM_ID,
            creation_date=date_helper.get_current_date(),
        )
        report = Report()
        report.__dict__.update(data_report)

        assert history.add_history(wallet, report)

        history.delete()

    def test_payment_wallet(self):
        data = dict(
            payment_id=self.PAYMENT_ID,
            hard_id=self.HARD_ID,
            name=self.TEST_STRING,
            user_id=self.USER_ID,
            discodes_id=self.DISCODES_ID,
            card_pan=self.CARD_PAN
        )
        self.model_test(PaymentWallet, data)

    def test_func_get_pid(self):
        wallet = PaymentWallet()
        wallet.get_pid(self.PIDS)

    def test_payment_account(self):
        data = dict(
            id=self.ACCOUNT_ID,
            firm_id=self.FIRM_ID,
            generated_date=datetime.strptime(
                self.TEST_DATE, "%Y-%m-%d %H:%M:%S"),
            summ=self.AMOUNT,
            items_count=self.ITEMS_COUNT,
            status=self.ACCOUNT_STATUS,
            filename=self.ACCOUNT_FILENAME,
            item_price=self.AMOUNT,
            gprs_terms_count=self.ITEMS_COUNT
        )
        self.model_test(PaymentAccount, data)

    def test_pdf_generator(self):
        data = dict(
            id=self.ACCOUNT_ID,
            firm_id=self.FIRM_ID,
            generated_date=datetime.strptime(
                self.TEST_DATE, "%Y-%m-%d %H:%M:%S"),
            summ=self.AMOUNT,
            items_count=self.ITEMS_COUNT,
            status=self.ACCOUNT_STATUS,
            filename=self.ACCOUNT_FILENAME,
            item_price=self.AMOUNT,
            gprs_terms_count=self.ITEMS_COUNT
        )

        account = PaymentAccount()
        account.__dict__.update(data)
        account.generate_pdf()
        filepath = "%s/%s" % (app.config['PDF_FOLDER'], account.filename)
        if not os.path.isfile("%s/%s" % (app.config['PDF_FOLDER'], account.filename)):
            assert False

        os.remove("%s/%s" % (app.config['PDF_FOLDER'], account.filename))

        assert True
