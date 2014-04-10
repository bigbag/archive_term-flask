# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel
from models.term import Term


class Event(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    key = db.Column(db.String(150), nullable=False)

    def get_by_key(self, key):
        return self.query.filter_by(key=key).first()

    def get_events(self, type=-1):
        if Term.TYPE_POS == type:
            return Event.query.filter(Event.key.in_(Term.EVENTS_POS))
        elif Term.TYPE_VENDING == type:
            return Event.query.filter(Event.key.in_(Term.EVENTS_VENDING))
        else:
            return Event.query.all()

    @cache.cached(timeout=600, key_prefix='all_events_list')
    def get_events_list(self):
        events = Event().get_events()
        result = {}
        for event in events:
            result[event.id] = event.name
        return result
