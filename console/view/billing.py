# -*- coding: utf-8 -*-
"""
    Консольное приложение для генерации и отправки счетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from datetime import datetime
from flask.ext.script import Command, Option

from web.tasks.accounts_send import AccountSenderTask


class Billing(Command):

    "Generate and send firm account"

    option_list = (
        Option('--firm_id', dest='firm_id'),
        Option('--date', dest='date', help='Format yyyy-mm-dd'),
        Option('--send', dest='send', default=False),
    )

    def run(self, firm_id, date, send):
        firm_id = int(firm_id)
        date = datetime.strptime(date, '%Y-%m-%d')
        print AccountSenderTask.account_generate(firm_id, date, send)
