# -*- coding: utf-8 -*-
"""
    Тест моделей

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest
from web import db
from web import app

from models.card_stack import CardStack
from models.mail_stack import MailStack
from models.report_stack import ReportStack
from models.user import User

from helpers import hash_helper


class ModelsCase(unittest.TestCase):

    TEST_STRING = 'Test'
    TEST_TEXT = 'Test test test'
    TEST_EMAIL = 'test1@test.ru'
    PAYMENT_ID = '00000000000000000001'
    TERM_ID = 21
    PERSON_ID = 1
    FIRM_ID = 8

    def model_test(self, Model, data):
        old = Model()
        old.__dict__.update(data)

        assert old.save()
        new = Model.query.get(old.id)
        old.delete()
        assert not Model.query.get(new.id)

    def test_card_stack(self):

        data = dict(
            term_id=self.TERM_ID,
            payment_id=self.PAYMENT_ID
        )
        self.model_test(CardStack, data)

    def test_mail_stack(self):
        data = dict(
            senders=self.TEST_EMAIL,
            recipients=self.TEST_EMAIL,
            subject=self.TEST_STRING,
            body=self.TEST_TEXT,
            attach='test.img',
        )
        self.model_test(MailStack, data)

    def test_report_stack(self):
        data = dict(
            email=self.TEST_EMAIL,
            person=self.PERSON_ID,
            firm_id=self.FIRM_ID,
            start='2013-08-01',
            stop='2013-08-10',
            type_id=1,
        )
        self.model_test(ReportStack, data)

    def test_user(self):
        data = dict(
            email=self.TEST_EMAIL,
            password=self.TEST_STRING,
        )
        self.model_test(User, data)
