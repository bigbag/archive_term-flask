# -*- coding: utf-8 -*-
"""
Модель Терминал

"""
import json
from api import app
from api import db


class Term(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'term'

    STATUS_VALID = 1
    STATUS_BANNED = -1

    TYPE_POS = 0
    TYPE_VENDING = 1

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, default=TYPE_POS)
    name = db.Column(db.String(300), nullable=False)
    tz = db.Column(db.String(300), default=app.config['TZ'])
    blacklist = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, index=True, default=STATUS_VALID)
    report_date = db.Column(db.DateTime)
    upload = db.Column(
        db.String(256),
        default={"start": "00:00:00",
                 "stop": "23:59:59"})
    upload_period = db.Column(db.Integer, default=0)
    download = db.Column(
        db.String(256),
        default={"start": "00:00:00",
                 "stop": "23:59:59"})
    download_period = db.Column(db.Integer, default=0)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_term(self):
        term = Term.query.filter_by(
            id=self.id,
            status=self.STATUS_VALID).first()

        return term

    def delete(self):
        db.session.delete(me)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
