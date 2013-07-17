# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска консольных приложений

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.script import Manager
from console import app
from console.view.report_generation import ReportGeneration
from console.view.mail_send import MailSend
from console.view.payment_info import PaymentInfo
from console.view.payment_recurrent import PaymentRecurrent

manager = Manager(app)

manager.add_command('report_gen', ReportGeneration())
manager.add_command('mail', MailSend())
manager.add_command('payment_info', PaymentInfo())
manager.add_command('payment_recurrent', PaymentRecurrent())
manager.run()
