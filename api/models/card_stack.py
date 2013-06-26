# -*- coding: utf-8 -*-
"""
Модель стека карт ожидающих привязки

"""
from api import db
from api.models.term import Term
from api.helpers.date_helper import *


class CardStack(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'card_stack'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    payment_id = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def update(self):
        db.session.commit()

    def save(self):
        if not self.creation_date:
            self.creation_date = get_curent_date()
        db.session.add(self)
        db.session.commit()
