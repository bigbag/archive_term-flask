# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска косольных приложений

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.script import Manager
from console import app
from console.view.report_generation import ReportGeneration
from console.view.mail_send import MailSend

manager = Manager(app)

manager.add_command('report', ReportGeneration())
manager.add_command('mail', MailSend())
manager.run()
