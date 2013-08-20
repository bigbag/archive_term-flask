# -*- coding: utf-8 -*-
"""
    Консольное приложение для тестирования и отладки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import random
import csv

from flask.ext.script import Command
from web.models.person import Person

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

        return spamreader

    def run(self):
        print self.rate(5, 36)
        print self.rate(6, 45)
        print self.rate(7, 49)
        #
        # for row in spamreader:
                # person = Person.query.filter_by(
                #     payment_id=row[1]).first()

                # if person.payment_id == person.hard_id:
                #     person.hard_id = row[0]
                #     print person.save()
