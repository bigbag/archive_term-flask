# -*- coding: utf-8 -*-
"""
    Модель для ДИС

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app


class SpotDis(db.Model):

    __bind_key__ = 'mobispot'
    __tablename__ = 'discodes'

    PREMIUM_NO = 0
    PREMIUM_YES = 1

    STATUS_INIT = 0
    STATUS_GENERATED = 1

    id = db.Column(db.Integer, primary_key=True)
    premium = db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.status = self.STATUS_GENERATED

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_new_list(self, count=10, premium=0):
        return self.query.filter_by(
            premium=premium,
            status=self.STATUS_INIT).limit(count).all()

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
