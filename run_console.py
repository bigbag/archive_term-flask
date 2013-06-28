# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска косольных приложений

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.script import Manager
from console import app
from console.view.report import Report
from console.view.mail import Mail

manager = Manager(app)

manager.add_command('report', Report())
manager.add_command('mail', Mail())
manager.run()
