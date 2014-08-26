# -*- coding: utf-8 -*-
"""
    Модель событий для которых установлены
    таймауты обслуживания для каждого пользователя


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json

from web import db

from models.base_model import BaseModel
from models.payment_loyalty import PaymentLoyalty
from models.payment_wallet import PaymentWallet
from models.person import Person


class PersonEvent(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'person_event'

    STATUS_ACTIVE = 1
    STATUS_BANNED = 0

    LIKE_TIMEOUT = 100000

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Event')
    timeout = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.timeout = 5
        self.status = self.STATUS_ACTIVE

    @staticmethod
    def get_valid_by_term_id(term_id):
        return PersonEvent.query.filter_by(term_id=term_id).all()

    @staticmethod
    def get_by_person_id(person_id):
        return PersonEvent.query.filter_by(person_id=person_id).all()

    @staticmethod
    def set_status_by_person_id(person_id, status):
        person_events = PersonEvent.get_by_person_id(person_id)
        for person_event in person_events:
            person_event.status = status
            db.session.add(person_event)

        db.session.commit()

    @staticmethod
    def add_by_user_loyalty_id(user_id, loyalty_id):
        loyalty = PaymentLoyalty.query.filter_by(
            id=loyalty_id).first()
        wallet = PaymentWallet.query.filter_by(
            user_id=user_id).first()
        if loyalty and wallet:
            person = Person.query.filter_by(
                firm_id=loyalty.firm_id, payment_id=wallet.payment_id).first()

            if not person:
                person = Person()
                person.name = 'Участник промо-кампании'
                person.firm_id = loyalty.firm_id
                person.hard_id = wallet.hard_id
                person.payment_id = wallet.payment_id
                person.save()

            answer = -1
            if loyalty.terms_id:
                terms = json.loads(loyalty.terms_id)
                for term in terms:
                    event = PersonEvent.query.filter_by(
                        person_id=person.id, term_id=term, event_id=loyalty.event_id, firm_id=loyalty.firm_id).first()

                if event:
                    if event.timeout > PersonEvent.LIKE_TIMEOUT:
                        event.status = PersonEvent.STATUS_BANNED
                        event.save()
                else:
                    event = PersonEvent()
                    event.person_id = person.id
                    event.term_id = term
                    event.event_id = loyalty.event_id
                    event.firm_id = loyalty.firm_id
                    event.timeout = PersonEvent.LIKE_TIMEOUT
                    event.save()
                    answer = event.id

            return answer

    @staticmethod
    def delete_by_user_loyalty_id(user_id, loyalty_id):
        loyalty = PaymentLoyalty.query.filter_by(
            id=loyalty_id).first()
        wallet = PaymentWallet.query.filter_by(
            user_id=user_id).first()
        if loyalty and wallet:
            person = Person.query.filter_by(
                firm_id=loyalty.firm_id, payment_id=wallet.payment_id).first()

            if not person:
                return False

            if loyalty.terms_id:
                terms = json.loads(loyalty.terms_id)
                for term in terms:
                    event = PersonEvent.query.filter_by(
                        person_id=person.id, term_id=term, event_id=loyalty.event_id, firm_id=loyalty.firm_id).first()

                if event:
                    event.delete()

            return True
