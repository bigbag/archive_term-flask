# -*- coding: utf-8 -*-
"""
    Модель реализующая принадлежность терминалов к фирмам и мультиаренду

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web import app
from models.term import Term
from models.firm import Firm

from helpers import date_helper


class FirmTerm(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'firm_term'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship(
        'Firm',
        primaryjoin="Firm.id==FirmTerm.firm_id")
    child_firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    child_firm = db.relationship(
        'Firm',
        primaryjoin="Firm.id==FirmTerm.child_firm_id")

    creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self):
        self.creation_date = date_helper.get_curent_date()

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_list_by_term_id(self, term_id):
        firm_terms = self.query.filter_by(
            term_id=term_id).all()

        firm_id_list = []
        for firm_term in firm_terms:
            firm_id_list.append(firm_term.child_firm_id)

        return firm_id_list

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
