# -*- coding: utf-8 -*-
"""
    Модель стека карт ожидающих привязки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web import app
from models.term import Term
from helpers import date_helper


class CardStack(db.Model):

    __bind_key__ = 'stack'
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    payment_id = db.Column(db.String(20), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.creation_date = date_helper.get_curent_date()

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            self.payment_id = str(self.payment_id).rjust(20, '0')
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
