# -*- coding: utf-8 -*-
"""
    Класс сообщения для отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask.ext.mail import Message


class ReportMessage(Message):

    def __init__(self, **kwargs):
        required = ['to', 'results']
        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                app.logger.error(msg)
                raise KeyError(msg)
        title = u"Отчет"
        results = kwargs['results']
        if 'interval' in results and 'firm_name' in results:
            title = 'Отчет, %s' % (results['interval'])
        Message.__init__(self, title)

        results = kwargs['results']

        self.add_recipient(kwargs['to'])
        self.html = render_template(
            'term/emails/report/general.html',
            **kwargs)

        filename = False
        if 'attach' in kwargs:
            filename = kwargs['attach']

        if filename:
            with open(filename, 'r') as fp:
                self.attach(
                    title,
                    "application/vnd.ms-excel",
                    fp.read())
