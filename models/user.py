# -*- coding: utf-8 -*-
"""
    Модель для пользователей


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel
from helpers import date_helper, hash_helper


class User(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'user'

    STATUS_NOACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_VALID = 2
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    activkey = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    lastvisit = db.Column(db.DateTime)
    status = db.Column(db.Integer, index=True)
    lang = db.Column(db.String(128), nullable=False)

    def __init__(self):
        self.lang = "en"
        self.creation_date = date_helper.get_curent_date()
        self.status = self.STATUS_NOACTIVE

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def save(self):
        self.password = hash_helper.get_password_hash(self.password)
        self.activkey = hash_helper.get_activkey(self.password)
        return BaseModel.save(self)
