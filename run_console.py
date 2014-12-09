# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска консольных приложений

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask.ext.script import Manager
from console import app
from console.view.billing import Billing
from console.view.test import TestCommand

manager = Manager(app)

manager.add_command('billing', Billing())
manager.add_command('test', TestCommand())
manager.run()
