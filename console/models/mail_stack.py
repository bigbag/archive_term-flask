# -*- coding: utf-8 -*-
"""
    Модель для очереди почтовых сообщений

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from console import db


class MailStack(db.Model):

    __bind_key__ = 'stack'
    __tablename__ = 'mail'

    LOCK_FREE = 0
    LOCK_SET = 1

    id = db.Column(db.Integer, primary_key=True)
    senders = db.Column(db.Text, nullable=False)
    recipients = db.Column(db.Text, nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    attach = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, nullable=False)
    lock = db.Column(db.Integer, index=True, default=LOCK_FREE)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        if not self.creation_date:
            self.creation_date = get_curent_date()
        db.session.add(self)
        db.session.commit()
