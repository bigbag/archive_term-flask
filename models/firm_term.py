# -*- coding: utf-8 -*-
"""
    Модель реализующая принадлежность терминалов к фирмам и мультиаренду

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app, db
from helpers import date_helper

from models.base_model import BaseModel


class FirmTerm(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'firm_term'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), index=True)
    term = db.relationship('Term')
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'), index=True)
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

    @staticmethod
    def get_list_by_term_id(term_id):
        firm_terms = FirmTerm.query.filter_by(
            term_id=term_id).all()

        return list(set(firm_term.child_firm_id for firm_term in firm_terms))

    @staticmethod
    def get_list_by_firm_id(firm_id, child=True):
        query = FirmTerm.query
        if child:
            query = query.filter_by(child_firm_id=firm_id)
        else:
            query = query.filter_by(firm_id=firm_id)

        firm_id_list = set()
        firm_terms = query.all()
        for firm_term in firm_terms:
            firm_id_list.add(firm_term.term_id)

        return firm_id_list

    @staticmethod
    def get_access_by_firm_id(firm_id, term_id):
        result = False
        access = FirmTerm.query.filter_by(
            firm_id=firm_id).filter_by(term_id=term_id).first()

        if access:
            result = True

        return result

    def to_json(self):
        date_pattern = '%H:%M %d.%m.%Y'
        creation_date = date_helper.from_utc(
            self.creation_date,
            app.config['TZ'])

        items = dict(
            id=self.id,
            term_id=self.term_id,
            firm_id=self.firm_id,
            child_firm_id=self.child_firm_id,
            child_firm_name=self.child_firm.name,
            creation_date=creation_date.strftime(date_pattern)

        )
        return items

    def term_remove(self):
        from models.term_event import TermEvent
        from models.person_event import PersonEvent

        term_events = TermEvent.query.filter_by(term_id=self.term_id).all()
        for term_event in term_events:
            PersonEvent(
            ).query.filter_by(
                term_id=self.term_id,
                firm_id=self.child_firm_id,
                event_id=term_event.event_id).delete()
        self.delete()

        return True
