# -*- coding: utf-8 -*-
"""
    Модель для ДИС

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from sqlalchemy.sql import func

from web import db

from models.base_model import BaseModel


class SpotDis(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'discodes'

    PREMIUM_NO = 0
    PREMIUM_YES = 1

    STATUS_INIT = 0
    STATUS_GENERATED = 1

    id = db.Column(db.Integer, primary_key=True)
    premium = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.status = self.STATUS_GENERATED

    def get_new_list(self, count=10, premium=0):
        return self.query.filter_by(
            premium=premium,
            status=self.STATUS_INIT).order_by(func.random()).limit(count).all()

    def set_generated(self):
        self.status = SpotDis.STATUS_GENERATED
        return self.save()

    def set_init(self):
        self.status = SpotDis.STATUS_INIT
        return self.save()
