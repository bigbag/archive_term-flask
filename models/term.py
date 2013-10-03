# -*- coding: utf-8 -*-
"""
    Модель для платежных и вендинговых терминалов


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import json, g
from web import app, db, cache
from helpers import date_helper

from models.firm_term import FirmTerm


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
    blacklist = db.Column(db.Integer)
    status = db.Column(db.Integer, index=True)
    report_date = db.Column(db.DateTime)
    config_date = db.Column(db.DateTime)
    blacklist_date = db.Column(db.DateTime)
    upload_start = db.Column(db.String(256))
    upload_stop = db.Column(db.String(256))
    upload_period = db.Column(db.Integer, nullable=False)
    download_start = db.Column(db.String(256))
    download_stop = db.Column(db.String(256))
    download_period = db.Column(db.Integer, nullable=False)
    version = db.Column(db.String(128))

    # def __init__(self):
    #     self.type = self.TYPE_VENDING
    #     self.upload = {"start": "00:00:00", "stop": "23:59:59"}
    #     self.upload_period = 0
    #     self.download = {"start": "00:00:00", "stop": "23:59:59"}
    #     self.tz = app.config['TZ']
    #     self.blacklist = 0
    #     self.status = self.STATUS_VALID

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_valid_term(self, term_id):
        return self.query.filter_by(
            id=term_id,
            status=self.STATUS_VALID).first()

    @cache.cached(timeout=600, key_prefix='term_by_id')
    def get_by_id(self, id):
        return self.query.get(id)

    def get_xml_view(self):
        self.tz = date_helper.get_timezone(self.tz)

        if self.type == self.TYPE_VENDING:
            self.type = 'Vending'
        elif self.type == self.TYPE_POS:
            self.type = 'Normal'
        return self

    def get_db_view(self):
        if self.type == 'Vending':
            self.type = self.TYPE_VENDING
        elif self.type == 'Normal':
            self.type = self.TYPE_POS
        return self

    @cache.cached(timeout=120, key_prefix='select_term_list')
    def select_term_list(self, firm_id, **kwargs):
        tz = app.config['TZ']
        date_pattern = '%H:%M %d.%m.%y'

        order = kwargs['order'] if 'order' in kwargs else 'id desc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        firm_term = FirmTerm().get_list_by_firm_id(firm_id)
        g.firm_term = firm_term

        query = Term.query.filter(Term.id.in_(firm_term))
        terms = query.paginate(page, limit, False).items

        result = []
        for term in terms:
            firm_general = FirmTerm().query.filter_by(term_id=term.id).first()
            data = dict(
                term_id=term.id,
                name=term.name,
                firm=firm_general.firm.name,
                status='active' if term.status == self.STATUS_VALID else '',
            )

            result.append(data)

        value = dict(
            terms=result,
            count=query.count(),
        )

        return value

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
