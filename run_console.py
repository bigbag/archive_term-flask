# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска консольных приложений

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask.ext.script import Manager
from console import app
from console.view.mail_send import MailSend
from console.view.report_parser import ReportParser
from console.view.payment_info import PaymentInfo
from console.view.payment_auto import PaymentAuto
from console.view.test import TestCommand
from console.view.check_likes import CheckLikes

manager = Manager(app)

manager.add_command('mail', MailSend())
manager.add_command('report_parser', ReportParser())
manager.add_command('payment_info', PaymentInfo())
manager.add_command('payment_auto', PaymentAuto())
manager.add_command('test', TestCommand())
manager.add_command('check_likes', CheckLikes())
manager.run()
