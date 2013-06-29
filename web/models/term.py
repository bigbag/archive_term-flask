# -*- coding: utf-8 -*-
"""
    Модель для платежных и вендинговых терминалов


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json
from web import app
from web import db


class Term(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'term'

    STATUS_VALID = 1
    STATUS_BANNED = -1

    TYPE_POS = 0
    TYPE_VENDING = 1

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    tz = db.Column(db.String(300), nullable=False)
    blacklist = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, index=True)
    report_date = db.Column(db.DateTime, nullable=False)
    upload = db.Column(db.String(256), nullable=False)
    upload_period = db.Column(db.Integer, nullable=False)
    download = db.Column(db.String(256), nullable=False)
    download_period = db.Column(db.Integer, nullable=False)

    def __init__(self, id):
        self.id = id
        self.type = self.TYPE_POS
        self.upload = {"start": "00:00:00", "stop": "23:59:59"}
        self.upload_period = 0
        self.download = {"start": "00:00:00", "stop": "23:59:59"}
        self.tz = app.config['TZ']
        self.blacklist = 0
        self.status = self.STATUS_VALID

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_term(self):
        term = Term.query.filter_by(
            id=self.id,
            status=self.STATUS_VALID).first()

        return term

    def get_xml_view(self):
        self.download = json.loads(self.download)
        self.upload = json.loads(self.upload)

        if self.type == self.TYPE_VENDING:
            self.type = 'Vending'
        elif term.type == self.TYPE_POS:
            self.type = 'Normal'
        return self

    def get_db_view(self):
        if self.type == 'Vending':
            self.type = self.TYPE_VENDING
        elif term.type == 'Normal':
            self.type = self.TYPE_POS
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
