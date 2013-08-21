# -*- coding: utf-8 -*-
"""
    Модель событий для которых установлены
    таймауты обслуживания для каждого пользователя


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import db
from web import app
from web.models.term import Term
from web.models.event import Event
from web.models.person import Person


class PersonEvent(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'person_event'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    firm_id = db.Column(db.Integer, index=True)
    timeout = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.timeout = "0"

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_all_events(self):
        return Event.query.all()

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
