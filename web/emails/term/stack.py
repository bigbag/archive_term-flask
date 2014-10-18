# -*- coding: utf-8 -*-
"""
    Класс сообщения для стека

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.mail import Message


class StackMessage(Message):

    @classmethod
    def desc(cls):
        return 'stack'

    def __init__(self, **kwargs):
        required = ['to', 'body', 'subject']

        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                raise KeyError(msg)

        Message.__init__(self, kwargs['subject'])

        self.add_recipient(kwargs['to'])
        self.html = kwargs['body']
