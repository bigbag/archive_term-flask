# -*- coding: utf-8 -*-
"""
    Модель стека карт ожидающих привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from helpers import date_helper

from models.base_model import BaseModel


class CardStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    payment_id = db.Column(db.String(20), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.creation_date = date_helper.get_current_date()

    def save(self):
        self.payment_id = str(self.payment_id).rjust(20, '0')
        return BaseModel.save(self)
