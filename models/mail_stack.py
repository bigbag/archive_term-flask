# -*- coding: utf-8 -*-
"""
    Модель для очереди почтовых сообщений

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json
from web import db
from helpers import date_helper

from models.base_model import BaseModel


class MailStack(db.Model, BaseModel):

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
    lock = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self):
        self.lock = self.LOCK_FREE
        self.creation_date = date_helper.get_curent_date()

    def get_json(self):
        self.senders = json.loads(self.senders)
        self.recipients = json.loads(self.recipients)
        return self

    @staticmethod
    def get_new():
        return MailStack.query.filter_by(lock=MailStack.LOCK_FREE).all()
