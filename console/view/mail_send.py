# -*- coding: utf-8 -*-
"""
    Консольное приложение для отправки писем

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json
from flask import Flask, render_template
from flask.ext.mail import Message
from flask.ext.script import Command

from console import mail
from models.mail_stack import MailStack


class MailSend(Command):

    MAIL_COUNT = 100

    "Sending mail"

    def run(self):

        with mail.connect() as conn:
            for i in xrange(0, self.MAIL_COUNT):
                email = MailStack.query.filter_by(
                    lock=MailStack.LOCK_FREE).first()

                if not email:
                    return False

                email.lock = MailStack.LOCK_SET
                email.save()

                senders = json.loads(email.senders)['email']
                recipients = json.loads(email.recipients)['email']
                for recipient in recipients:
                    msg = Message(
                        email.subject,
                        sender=senders,
                        recipients=[recipient])

                    msg.html = email.body
                    conn.send(msg)

                email.delete()

        return True
