# -*- coding: utf-8 -*-
"""
    Модель для профилей пользователей


    :copyright: (c) 2015 by Amelin Denis.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class UserProfile(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'user_profile'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    city = db.Column(db.String(300))
    sex = db.Column(db.Integer)
    birthday = db.Column(db.String(10))
    photo = db.Column(db.Text, nullable=False)
