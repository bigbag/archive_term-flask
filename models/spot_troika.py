# -*- coding: utf-8 -*-
"""
    Модель для спотов связанных с картой тройка

    :copyright: (c) 2015 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from models.base_model import BaseModel


class SpotTroika(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot_troika'

    discodes_id = db.Column(db.Integer, primary_key=True)
