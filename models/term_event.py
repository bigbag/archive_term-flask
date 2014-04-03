# -*- coding: utf-8 -*-
"""
    Модель событий привязанных к терминалу

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel
from models.person_event import PersonEvent
from models.firm_term import FirmTerm
from models.person import Person


class TermEvent(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'term_event'

    DEFAULT_MIN_ITEM = 0
    DEFAULT_MAX_ITEM = 65535

    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    start = db.Column(db.String(10), nullable=False)
    stop = db.Column(db.String(10), nullable=False)
    min_item = db.Column(db.Integer, nullable=False)
    max_item = db.Column(db.Integer, nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    credit_period = db.Column(db.Integer, nullable=False)
    credit_amount = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.cost = 0
        self.age = 0
        self.start = "00:01"
        self.stop = "23:59"
        self.timeout = 5
        self.min_item = self.DEFAULT_MIN_ITEM
        self.max_item = self.DEFAULT_MAX_ITEM
        self.event_id = 1
        self.credit_period = 900
        self.credit_amount = 50000

    def term_event_save(self, firm_id, term_id):
        result = False

        PersonEvent.query.filter_by(
            term_id=term_id,
            firm_id=firm_id,
            event_id=self.event_id).delete()

        persons = Person.query.filter_by(firm_id=firm_id).all()
        for person in persons:
            person_event = PersonEvent()
            person_event.person_id = person.id
            person_event.term_id = term_id
            person_event.event_id = self.event_id
            person_event.firm_id = firm_id
            person_event.timeout = self.timeout
            db.session.add(person_event)

        db.session.commit()
        result = True

        return result

    def term_event_remove(self, firm_id):
        PersonEvent.query.filter_by(
            term_id=self.term_id,
            firm_id=firm_id,
            event_id=self.event_id).delete()

        self.delete()
        return True

    def get_by_term_id(self, term_id):
        return self.query.filter_by(term_id=term_id).all()

    def get_by_firm_id(self, firm_id):
        firm_term = FirmTerm().get_list_by_firm_id(firm_id)
        return self.query.filter(
            TermEvent.term_id.in_(
                firm_term)).all()

    def save(self):
        return BaseModel.save(self)
