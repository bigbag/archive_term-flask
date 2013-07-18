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
from web.models.mail_stack import MailStack


class MailSend(Command):

    "Sending mail"

    def run(self):

        emails = MailStack.query.filter_by(
            lock=MailStack.LOCK_FREE).limit(
                100).all()

        with mail.connect() as conn:
            for email in emails:
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
