# -*- coding: utf-8 -*-
"""
    Модель для таблицы связей кошелёк<->акция

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from helpers import date_helper


class WalletLoyalty(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'wallet_loyalty'

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer)
    loyalty_id = db.Column(db.Integer)
    summ = db.Column(db.String(50))
    count = db.Column(db.Integer)
    part_count = db.Column(db.Integer)
    bonus_count = db.Column(db.Integer)

    def __repr__(self):
        return '<id %r>' % (self.id)

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
