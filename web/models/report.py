# -*- coding: utf-8 -*-
"""
    Модель отчетов поступающих с терминалов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.term import Term
from web.models.person import Person
from web.models.firm import Firm


class Report(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()
