# -*- coding: utf-8 -*-
"""
    Тест моделей терминального проекта

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest
from web import db
from web import app

from models.event import Event
from models.firm import Firm
from models.firm_term import FirmTerm
from models.person import Person
from models.person_event import PersonEvent
from models.report import Report
from models.spot import Spot
from models.spot_dis import SpotDis

from helpers import date_helper


class ModelsTermCase(unittest.TestCase):

    TEST_STRING = 'Test'
    TEST_TEXT = 'Test test test'
    TEST_EMAIL = 'test1@test.ru'
    TERM_ID = 21
    PERSON_ID = 1
    FIRM_ID = 8
    EVENT_ID = 3
    HARD_ID = '9995749700230784'
    PAYMENT_ID = '99999999999999999999'
    PERSON_ID = 1
    USER_ID = 1
    DISCODES_ID = 999999

    def model_test(self, Model, data):
        old = Model()
        old.__dict__.update(data)

        assert old.save()
        new = Model.query.get(old.id)
        old.delete()
        assert not Model.query.get(new.id)

    def test_event(self):
        data = dict(
            name=self.TEST_STRING,
            key=self.TEST_STRING
        )
        self.model_test(Event, data)

    def test_firm(self):
        data = dict(
            name=self.TEST_STRING,
            inn=self.TEST_STRING,
            sub_domain=self.TEST_STRING,
            email=self.TEST_EMAIL
        )
        self.model_test(Firm, data)

    def test_firm_term(self):
        data = dict(
            term_id=self.TERM_ID,
            firm_id=self.FIRM_ID,
            child_firm_id=self.FIRM_ID
        )
        self.model_test(FirmTerm, data)

    def test_person(self):
        data = dict(
            first_name=self.TEST_STRING,
            firm_id=self.FIRM_ID,
            payment_id=self.PAYMENT_ID,
            hard_id=self.HARD_ID
        )
        self.model_test(Person, data)

    def test_person_event(self):
        data = dict(
            person_id=self.PERSON_ID,
            term_id=self.TERM_ID,
            event_id=self.EVENT_ID,
            firm_id=self.FIRM_ID
        )
        self.model_test(PersonEvent, data)

    def test_report(self):
        data = dict(
            term_id=self.TERM_ID,
            event_id=self.PERSON_ID,
            person_id=self.EVENT_ID,
            payment_id=self.FIRM_ID,
            firm_id=self.FIRM_ID,
            creation_date=date_helper.get_curent_date(),
        )
        self.model_test(Report, data)

    def test_spot(self):
        data = dict(
            discodes_id=999999,
            user_id=self.USER_ID,
            premium=0,
        )
        old = Spot()
        old.__dict__.update(data)

        assert old.save()
        new = Spot.query.get(old.discodes_id)
        old.delete()
        assert not Spot.query.get(new.discodes_id)

    def test_func_get_code(self):
        spot = Spot()
        assert spot.get_code(self.DISCODES_ID)

    def test_func_get_barcode(self):
        spot = Spot()
        assert spot.get_barcode()

    def test_func_get_url(self):
        spot = Spot()
        assert spot.get_url()
