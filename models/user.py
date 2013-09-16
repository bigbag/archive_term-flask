# -*- coding: utf-8 -*-
"""
    Модель для пользователей


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app
from helpers import date_helper, hash_helper


class User(db.Model):

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

    def __repr__(self):
        return '<User %r>' % (self.email)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            if not self.activkey:
                self.password = hash_helper.get_password_hash(self.password)
            self.activkey = hash_helper.get_activkey(self.password)
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
