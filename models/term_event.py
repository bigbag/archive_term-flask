# -*- coding: utf-8 -*-
"""
    Модель событий привязанных к терминалу

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app
from models.term import Term
from models.event import Event


class TermEvent(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'term_event'

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    start = db.Column(db.String(10), nullable=False)
    stop = db.Column(db.String(10), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')

    def __init__(self):
        self.cost = 0
        self.age = 0
        self.start = "00:01"
        self.stop = "23:59"
        self.timeout = 0
        self.event_id = 1

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_by_term_id(self, term_id):
        return self.query.filter_by(term_id=term_id).all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
