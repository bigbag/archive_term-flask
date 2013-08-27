# -*- coding: utf-8 -*-
"""
    Консольное приложение для тестирования и отладки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import random
import csv
import uuid
from flask.ext.script import Command
from models.person import Person
from models.payment_wallet import PaymentWallet
from models.person_event import PersonEvent

from console.configs.payment import UnitellerConfig
from libs.uniteller_api import UnitellerApi


class TestCommand(Command):

    def rate(self, count, all):
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

    def run(self):
        print True

        # with open('tmp/import.csv', 'rb') as csvfile:
        #     spamreader = csv.reader(csvfile)
        #     for row in spamreader:
        #         person = Person.query.filter_by(payment_id=row[1]).first()

        #         if person:
        #             continue

        #         person = Person()
        #         person.hard_id = row[0]
        #         person.payment_id = row[1]
        #         person.firm_id = 12
        #         person.first_name = row[3]
        #         person.last_name = row[2]

        #         if not person.save():
        #             continue

        #         person_event = PersonEvent()
        #         person_event.person_id = person.id
        #         person_event.term_id = 39
        #         person_event.event_id = 3
        #         person_event.firm_id = person.firm_id
        #         person_event.timeout = "00:05:00"
        #         person_event.save()

        #         person_event = PersonEvent()
        #         person_event.person_id = person.id
        #         person_event.term_id = 48
        #         person_event.event_id = 3
        #         person_event.firm_id = person.firm_id
        #         person_event.timeout = "00:05:00"
        #         person_event.save()

          # for row in spamreader:
        #     person = Person.query.filter_by(
        #         payment_id=row[1]).first()
        #     if person.payment_id == person.hard_id:
        #         person.hard_id = row[0]
        #         print person.save()
        # print self.rate(5, 36)
        # print self.rate(6, 45)
        # print self.rate(7, 49)
