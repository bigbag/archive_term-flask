# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel
from models.event_type import EventType


class Event(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    key = db.Column(db.String(150), nullable=False)

    def get_by_key(self, key):
        return self.query.filter_by(key=key).first()

    @cache.cached(timeout=600, key_prefix='all_events_dict')
    def get_dict(self):
        events = Event.query.all()
        result = {}
        for event in events:
            result[event.id] = event.name
        return result
