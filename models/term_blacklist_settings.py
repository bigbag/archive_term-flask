# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class BlacklistSettings(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'blacklist_settings'

    STATUS_OFF = 0
    STATUS_ON = 1
    DEFAULT_TIMEOUT = 5  # 5 min

    term_id = db.Column(db.Integer, primary_key=True)
    partial_on_restart = db.Column(db.Integer)
    partial_timeout = db.Column(db.Integer)
    full_on_restart = db.Column(db.Integer)
    full_timeout = db.Column(db.Integer)

    def __init__(self):
        self.partial_on_restart = self.STATUS_ON
        self.partial_timeout = self.DEFAULT_TIMEOUT
        self.full_on_restart = self.STATUS_ON
        self.full_timeout = self.DEFAULT_TIMEOUT

    def __repr__(self):
        return '<term_id %r>' % (self.term_id)
