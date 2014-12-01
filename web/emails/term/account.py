# -*- coding: utf-8 -*-
"""
    Класс сообщения для счета

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""

from flask import render_template
from flask.ext.mail import Message


class AccountMessage(Message):

    @classmethod
    def desc(cls):
        return 'account'

    def __init__(self, **kwargs):
        required = ['to', 'date_text', 'attach']
        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                raise KeyError(msg)

        title = u'Счет за %s' % kwargs['date_text']
        Message.__init__(self, title)

        self.add_recipient(kwargs['to'])
        template = 'term/emails/report/account.html'
        self.html = render_template(template, **kwargs)

        filename = False
        if 'attach' in kwargs:
            filename = kwargs['attach']

        if filename:
            with open(filename, 'r') as fp:
                attach_name = '%s.pdf' % title
                self.attach(
                    attach_name,
                    "application/pdf",
                    fp.read())
