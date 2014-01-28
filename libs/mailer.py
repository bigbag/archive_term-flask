# -*- coding: utf-8 -*-
"""
    Обертка для отсылки писем

    :copyright: (c) 2013 by Martin Samson.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from flask.ext.mail import Mail, email_dispatched
from web.tasks.mail import send


class Mailer(Mail):

    def send(self, MessageClass, **kwargs):
        if app.config.get('USE_CELERY', False):
            task = send.delay(MessageClass, **kwargs)
            return True

        return Mail.send(self, MessageClass(**kwargs))
