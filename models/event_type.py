# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel


class EventType(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'event_type'

    id = db.Column(db.Integer, primary_key=True)
    term_type = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')

    @staticmethod
    def get_types(term_type=False):
        if isinstance(term_type, (bool)):
            return EventType.query.all()

        return EventType.query.filter_by(term_type=term_type).all()

    @staticmethod
    def get_dict(term_type=False):
        from models.event import Event

        types = EventType.get_types(term_type)
        events = Event.get_dict()
        result = {}
        for row in types:
            result[row.event_id] = events[row.event_id]
        return result
