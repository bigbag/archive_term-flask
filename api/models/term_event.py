# -*- coding: utf-8 -*-
"""
Модель событий привязанных к терминалу

"""
from api import db
from api.models.term import Term
from api.models.event import Event


class TermEvent(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'term_event'

    id = db.Column(db.Integer, primary_key=True)
    age_id = db.Column(db.Integer, default=1)
    cost = db.Column(db.Integer, default=0)
    start = db.Column(db.Time, default="00:00:00")
    stop = db.Column(db.Time, default="23:59:59")
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(me)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
