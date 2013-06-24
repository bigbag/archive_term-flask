# -*- coding: utf-8 -*-
"""
Модель сотрудников

"""
from api import db
from api.helpers.date_helper import *


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
    status = db.Column(db.Integer, default=1)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<id %r>' % (self.id)

    def save(self):
        if not self.creation_date:
            self.creation_date = get_curent_date()
        db.session.commit()
