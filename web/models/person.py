# -*- coding: utf-8 -*-
"""
    Модель для сотрудников фирм

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.helpers.date_helper import *


class Person(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'person'

    STATUS_VALID = 1
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    midle_name = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    tabel_id = db.Column(db.String(150))
    birthday = db.Column(db.Date())
    firm_id = db.Column(db.Integer, nullable=False)
    card = db.Column(db.String(8))
    payment_id = db.Column(db.String(32), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self, id):
        self.id = id
        self.status = self.STATUS_VALID

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            if not self.creation_date:
                self.creation_date = get_curent_date()
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            return False
        else:
            return True
