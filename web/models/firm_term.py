# -*- coding: utf-8 -*-
"""
    Модель реализующая принадлежность терминалов к фирмам и мультиаренду

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db


class FirmTerm(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'firm_term'

    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    child_firm_id = db.Column(db.Integer, db.ForeignKey('child_firm_id.id'))
    child_firm = db.relationship('Firm')

    def __init__(self, id):
        self.id = id
        self.child_firm_id = 0

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
