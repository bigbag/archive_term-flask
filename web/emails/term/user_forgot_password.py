# -*- coding: utf-8 -*-
"""
    Класс сообщения для восстановления пароля

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask.ext.mail import Message


class UserForgotPasswordMessage(Message):

    @classmethod
    def desc(cls):
        return 'recovery'

    def __init__(self, **kwargs):
        Message.__init__(self, "Восстановление пароля")

        required = ['to', 'recovery_url']
        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                raise KeyError(msg)

        self.add_recipient(kwargs['to'])
        self.body = render_template(
            'term/emails/user/forgot_password.txt',
            **kwargs)
        self.html = render_template(
            'term/emails/user/forgot_password.html',
            **kwargs)
