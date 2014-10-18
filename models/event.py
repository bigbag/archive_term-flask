# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel


class Event(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    key = db.Column(db.String(150), nullable=False)

    @staticmethod
    def get_by_key(key):
        return Event.query.filter_by(key=key).first()

    @staticmethod
    @cache.cached(timeout=600, key_prefix='all_events_dict')
    def get_dict():
        events = Event.query.all()
        result = {}
        for event in events:
            result[event.id] = event.name
        return result
