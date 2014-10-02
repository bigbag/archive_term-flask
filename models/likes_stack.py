# -*- coding: utf-8 -*-
"""
    Модель для очереди на проверку лайков в соцсетях

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class LikesStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'likes_stack'

    LOCK_FREE = 0
    LOCK_SET = 1

    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, nullable=False)
    loyalty_id = db.Column(db.Integer, nullable=False)
    sharing_id = db.Column(db.Integer, nullable=False)
    lock = db.Column(db.Integer, nullable=False)
    wl_id = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.lock = self.LOCK_FREE
