# -*- coding: utf-8 -*-
"""
    Модель для сотрудников фирм

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app, db, cache

from helpers import date_helper


class Person(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'person'

    STATUS_VALID = 1
    STATUS_BANNED = 0

    TYPE_TIMEOUT = 0
    TYPE_WALLET = 1

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    tabel_id = db.Column(db.String(150))
    birthday = db.Column(db.Date())
    firm_id = db.Column(db.Integer, nullable=False, index=True)
    card = db.Column(db.String(8))
    payment_id = db.Column(db.String(20), nullable=False, index=True)
    hard_id = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False, index=True)
    wallet_status = db.Column(db.Integer, nullable=False, index=True)
    type = db.Column(db.Integer, nullable=False, index=True)

    def __init__(self):
        self.status = self.STATUS_VALID
        self.wallet_status = self.STATUS_VALID
        self.type = self.TYPE_TIMEOUT
        self.creation_date = date_helper.get_curent_date()
        self.name = u'Пользователь'

    def select_person_list(self, firm_id, **kwargs):
        order = kwargs[
            'order'] if 'order' in kwargs else 'name asc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1
        status = kwargs['status'] if 'status' in kwargs else 1
        person_name = kwargs[
            'person_name'] if 'person_name' in kwargs else False

        query = Person.query.filter(Person.firm_id == firm_id)
        query = query.filter(Person.status == status)
        query = query.order_by(order)

        if person_name:
            query = query.filter(Person.name.like('%' + person_name + '%'))

        persons = query.paginate(page, limit, False).items

        result = []
        for person in persons:
            data = dict(
                id=person.id,
                name=person.name,
                card=person.card,
                wallet_status=int(person.wallet_status == self.STATUS_VALID),
                hard_id=int(person.payment_id) if person.payment_id else 0,
            )
            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )
        return value

    def __repr__(self):
        return '<id %r>' % (self.id)

    def person_remove(self):
        from models.term_corp_wallet import TermCorpWallet

        TermCorpWallet.query.filter_by(person_id=self.id).delete()

        self.delete()
        return True

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
