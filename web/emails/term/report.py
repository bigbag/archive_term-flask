# -*- coding: utf-8 -*-
"""
    Класс сообщения для отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask.ext.mail import Message


class ReportMessage(Message):

    @classmethod
    def desc(cls):
        return 'report'

    def __init__(self, **kwargs):
        required = ['to', 'result', 'template']
        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                app.logger.error(msg)
                raise KeyError(msg)
        title = u"Отчет"
        result = kwargs['result']
        if result.interval and result.firm.name:
            title = 'Отчет, %s' % result.interval['templ_interval']
        Message.__init__(self, title)

        result = kwargs['result']

        self.add_recipient(kwargs['to'])
        template = 'term/emails/report/%s.html' % kwargs['template']
        self.html = render_template(template, **kwargs)

        filename = False
        if 'attach' in kwargs:
            filename = kwargs['attach']

        if filename:
            with open(filename, 'r') as fp:
                attach_name = '%s.xlsx' % title
                self.attach(
                    attach_name,
                    "application/vnd.ms-excel",
                    fp.read())
