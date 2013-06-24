# -*- coding: utf-8 -*-
"""
Модель событий

"""
from api import db


class Event(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    key = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def save(self):
        db.session.commit()
