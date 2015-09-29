# -*- coding: utf-8 -*-
"""
    Модель для контента спотов

    :copyright: (c) 2015 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class SpotContent(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot_content'

    id = db.Column(db.Integer, primary_key=True)
    discodes_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    lang = db.Column(db.String(10))
    spot_type_id = db.Column(db.Integer)
    content = db.Column(db.Text())