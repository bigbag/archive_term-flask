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

    def get_types(self, term_type=False):
        if not term_type:
            return EventType.query.all()

        return EventType.query.filter_by(term_type=term_type).all()

    # @cache.cached(timeout=600, key_prefix='all_events_type_dict')
    def get_dict(self, term_type=False):
        types = EventType().get_types(term_type)
        result = {}
        for row in types:
            result[row.event_id] = row.event.name
        return result
