# -*- coding: utf-8 -*-
"""
    Модель для доступных администраторам терминалов


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel

from models.term_user import TermUser
from models.firm import Firm


class TermUserFirm(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'user_firm'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('term_user.id'))
    user = db.relationship(
        'TermUser',
        primaryjoin="TermUser.id==TermUserFirm.user_id")
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm', primaryjoin="Firm.id==TermUserFirm.firm_id")
