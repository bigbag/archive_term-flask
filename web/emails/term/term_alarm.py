# -*- coding: utf-8 -*-
"""
    Класс сообщения для уведомления о сбое

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask.ext.mail import Message


class TermAlarmMessage(Message):

    @classmethod
    def desc(cls):
        return 'term alarm'

    def __init__(self, **kwargs):
        required = ['to', 'term']
        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                raise KeyError(msg)

        term = kwargs['term']
        title = u'Оповещение о сбое, %s' % term.name
        Message.__init__(self, title)

        self.add_recipient(kwargs['to'])
        self.body = render_template(
            'term/emails/alarm/term_alarm.txt',
            **kwargs)
        self.html = render_template(
            'term/emails/alarm/term_alarm.html',
            **kwargs)
