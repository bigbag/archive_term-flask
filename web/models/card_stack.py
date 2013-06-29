# -*- coding: utf-8 -*-
"""
    Модель стека карт ожидающих привязки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.term import Term
from web.helpers.date_helper import *


class CardStack(db.Model):

    __bind_key__ = 'stack'
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    payment_id = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

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
