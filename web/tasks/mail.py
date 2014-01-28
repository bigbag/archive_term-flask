# -*- coding: utf-8 -*-
"""
	Задача отправки email

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from web.celery import celery

from flask.ext.mail import Mail


@celery.task
def send(MessageClass, **kwargs):
    with app.test_request_context() as request:
        mailer = Mail(app)
        mailer.send(MessageClass(**kwargs))
