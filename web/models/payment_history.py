# -*- coding: utf-8 -*-
"""
    Модель для платежной карты (кошелька)


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.models.term import Term


class PaymentWallet(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'history'

    STATUS_NEW = 0
    STATUS_COMPLETE = 1
    STATUS_FAILURE = -1

    TYPE_MINUS = -1
    TYPE_PLUS = 1

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), index=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    wallet = db.relationship('PaymentWallet')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'))
    term = db.relationship('Term')
    summ = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.Integer(), nullable=False)

    def __init__(self, id):
        self.status = self.STATUS_NEW

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        if not self.creation_date:
            self.creation_date = get_curent_date()
        db.session.add(self)
        db.session.commit()
