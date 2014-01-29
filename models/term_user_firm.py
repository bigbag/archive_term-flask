# -*- coding: utf-8 -*-
"""
    Модель для доступных администраторам терминалов


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db, app
from helpers import date_helper, hash_helper

from models.term_user import TermUser
from models.firm import Firm


class TermUserFirm(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'user_firm'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('term_user.id'))
    user = db.relationship(
        'TermUser',
        primaryjoin="TermUser.id==TermUserFirm.user_id")
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship(
        'Firm',
        primaryjoin="Firm.id==TermUserFirm.firm_id")

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
