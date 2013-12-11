# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app, db, cache


class Event(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    key = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_by_key(self, key):
        return self.query.filter_by(key=key).first()

    @cache.cached(timeout=600, key_prefix='all_events')
    def get_events(self):
        return self.query.all()

    @cache.cached(timeout=600, key_prefix='all_events_list')
    def get_events_list(self):
        events = Event().get_events()
        result = {}
        for event in events:
            result[event.id] = event.name
        return result

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
