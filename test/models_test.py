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
from models.payment_loyalty import PaymentLoyalty
from models.soc_token import SocToken
from models.likes_stack import LikesStack

from helpers import hash_helper


class ModelsCase(unittest.TestCase):

    TEST_STRING = 'Test'
    TEST_TEXT = 'Test test test'
    TEST_EMAIL = 'test1@test.ru'
    PAYMENT_ID = '00000000000000000001'
    TERM_ID = 21
    PERSON_ID = 1
    FIRM_ID = 8
    EVENT_ID = 3
    USER_ID = 1
    TOKEN_ID = 1
    LOYALTY_ID = 1

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

    def test_loyalty(self):
        data = dict(
            terms_id='[21]',
            event_id=self.EVENT_ID,
            firm_id=self.FIRM_ID,
            rules=0,
            interval=3,
            amount=8000,
            threshold=60000,
            desc='Тестовая акция',
            creation_date='2013-11-22 13:43:47',
            start_date='2013-10-30 18:07:40',
            stop_date='2014-04-30 18:07:40',
            img='defoult-store.png',
            part_limit=3,
        )
        self.model_test(PaymentLoyalty, data)

    def test_soc_token(self):
        data = dict(
            type=1,
            user_id=self.USER_ID,
            soc_id=100003300240179,
            soc_email=self.TEST_EMAIL,
            user_token='token',
            token_expires=1392539342
        )
        self.model_test(SocToken, data)

    def test_likes_stack(self):
        data = dict(
            token_id=self.TOKEN_ID,
            loyalty_id=self.LOYALTY_ID
        )
        self.model_test(LikesStack, data)
