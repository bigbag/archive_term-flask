# -*- coding: utf-8 -*-
"""
    Модель для рисунков на спотах

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from models.base_model import BaseModel


class SpotPattern(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot_pattern'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    show = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.show = 0
