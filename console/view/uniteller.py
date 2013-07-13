# -*- coding: utf-8 -*-
"""
    Консольное приложение работы с Uniteller

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask.ext.script import Command
from console.configs.payment import UnitellerConfig
from libs.uniteller_api import UnitellerApi


class Uniteller(Command):

    "Uniteller  interface"

    def run(self):

        un = UnitellerApi(UnitellerConfig)

        order = dict(
            order_id=115,
            amount=10,
            customer_id=10)

        print un.get_payment_sing(order)
