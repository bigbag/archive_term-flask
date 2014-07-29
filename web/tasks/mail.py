# -*- coding: utf-8 -*-
"""
	Задача отправки email

    :copyright: (c) 2014 by Pavel Lyashkov.
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

    if 'to' in kwargs:
        return "Mail type: %s, recipient: %s" % (MessageClass.desc(), kwargs['to'])

    return True

@celery.task
def mail_stack_sender():
    from models.mail_stack import MailStack
    from web.tasks import mail
    from web.emails.term.stack import StackMessage

    stack = MailStack.get_new()
    if not stack:
        return False

    for row in stack:
        row = row.get_json()
        for recipient in row.recipients:
            mail.send.delay(
                StackMessage,
                to=recipient,
                body=row.body,
                subject=row.subject)

        row.delete()

    return True

