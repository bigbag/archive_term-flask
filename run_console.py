# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска консольных приложений

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask.ext.script import Manager
from console import app
from console.view.billing import Billing
from console.view.report_parser import ReportParser
from console.view.test import TestCommand
from console.view.refresh_person_status import RefreshPersonStatus

manager = Manager(app)

manager.add_command('report_parser', ReportParser())
manager.add_command('billing', Billing())
manager.add_command('test', TestCommand())
manager.add_command('refresh_person_status', RefreshPersonStatus())
manager.run()
