# -*- coding: utf-8 -*-
"""
    Модель для очереди на проверку лайков в соцсетях

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db


class LikesStack(db.Model):

    __bind_key__ = 'stack'
    __tablename__ = 'likes_stack'

    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.Integer, nullable=False)
    loyalty_id = db.Column(db.Integer, nullable=False)

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
