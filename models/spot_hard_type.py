# -*- coding: utf-8 -*-
"""
    Модель для моделей спотов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from models.base_model import BaseModel


class SpotHardType(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot_hard_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    hard_id = db.Column(db.Integer, nullable=False)
    color_id = db.Column(db.Integer)
    pattern_id = db.Column(db.Integer)
    show = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(150), nullable=False)
    sort = db.Column(db.Integer)

    def __init__(self):
        self.show = 0
