# -*- coding: utf-8 -*-
"""
    Модель для корпоративной карты (кошелька)


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app
from helpers import date_helper


class TermCorpWallet(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'corp_wallet'

    STATUS_DISABLED = 0
    STATUS_ACTIVE = 1
    STATUS_BANNED = -1

    INTERVAL_ONCE = 0
    INTERVAL_WEEK = 1
    INTERVAL_MONTH = 2

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    creation_date = db.Column(db.DateTime, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    limit = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.Integer, nullable=False, index=True)

    def __init__(self):
        self.limit = 0
        self.balance = 0
        self.interval = self.INTERVAL_ONCE
        self.creation_date = date_helper.get_curent_date()
        self.status = self.STATUS_ACTIVE

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_interval_list(self):
        return [
            {'id': self.INTERVAL_ONCE, 'name': u"Нет"},
            {'id': self.INTERVAL_WEEK, 'name': u"Еженедельно"},
            {'id': self.INTERVAL_MONTH, 'name': u"Ежемесячно"}
        ]

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
