# -*- coding: utf-8 -*-
"""
    Консольное приложение для обновления статуса сотрудников

    :copyright: (c) 2015 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""

from flask.ext.script import Command, Option

from models.person import Person


class RefreshPersonStatus(Command):

    "Refresh person status"

    option_list = (
        Option('--firm_id', dest='firm_id', default=False),
        Option('--id', dest='id', default=False),
    )

    def run(self, firm_id, id):
        query = Person.query
        if firm_id:
            query = query.filter(Person.firm_id == int(firm_id))
        if id:
            query = query.filter(Person.id == int(id))

        persons = query.all()
        for person in persons:
            person.save()

        print "Status of %s persons refreshed" % query.count()
