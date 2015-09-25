# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, cache

from models.base_model import BaseModel


class Firm(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'firm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    inn = db.Column(db.String(50))
    sub_domain = db.Column(db.Text(), nullable=False, index=True)
    pattern_id = db.Column(db.String(200), nullable=False)
    logo = db.Column(db.Text())
    address = db.Column(db.Text())
    account_email = db.Column(db.Text())
    transaction_percent = db.Column(db.Integer()) # до сотых долей процента, 1% = 100
    transaction_comission = db.Column(db.Integer())
    legal_entity = db.Column(db.String(256))
    general_manager = db.Column(db.String(128))
    chief_accountant = db.Column(db.String(128))
    gprs_rate = db.Column(db.Integer())

    @staticmethod
    def get_by_sub_domain(sub_domain):
        return Firm.query.filter_by(sub_domain=sub_domain).first()

    @staticmethod
    @cache.cached(timeout=3600, key_prefix='all_firms_type_dict')
    def select_name_dict():
        firms = Firm.query.all()

        result = {}
        for firm in firms:
            result[firm.id] = firm.name

        return result
