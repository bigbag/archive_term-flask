# -*- coding: utf-8 -*-
"""
    Модель для администраторов терминалов


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel
from helpers import date_helper, hash_helper


class TermUser(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'term_user'

    GROUP_DEFAULT = 0
    GROUP_API = 1

    STATUS_NOACTIVE = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    activkey = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    group = db.Column(db.Integer, nullable=False)
    lastvisit = db.Column(db.DateTime)
    api_key = db.Column(db.String(150))
    api_secret = db.Column(db.String(150))
    status = db.Column(db.Integer, index=True)

    def __init__(self):
        self.group = self.GROUP_DEFAULT
        self.status = self.STATUS_NOACTIVE
        self.creation_date = date_helper.get_current_date()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @cache.cached(timeout=300)
    def get_by_api_key(self, api_key):
        return self.query.filter_by(api_key=api_key).first()

    @cache.cached(timeout=60)
    def get_by_email(self, email):
        return self.query.filter_by(email=email).first()

    @cache.cached(timeout=60)
    def get_by_id(self, id):
        return self.query.get(int(id))

    def get_change_password_url(self, url):
        return "%s/change/%s/%s" % (
            url,
            self.id,
            self.activkey)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        self.activkey = hash_helper.get_activkey(self.password)
        return BaseModel.save(self)
