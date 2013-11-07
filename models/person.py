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
    STATUS_BANNED = -1

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    midle_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    tabel_id = db.Column(db.String(150))
    birthday = db.Column(db.Date())
    firm_id = db.Column(db.Integer, nullable=False)
    card = db.Column(db.String(8))
    payment_id = db.Column(db.String(20), nullable=False)
    hard_id = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.status = self.STATUS_VALID
        self.creation_date = date_helper.get_curent_date()

    @cache.cached(timeout=5, key_prefix='select_term_list')
    def select_person_list(self, firm_id, **kwargs):
        order = kwargs[
            'order'] if 'order' in kwargs else 'last_name asc, first_name asc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1
        status = kwargs['status'] if 'status' in kwargs else 1

        query = Person.query.filter(Person.firm_id == firm_id)
        query = query.filter(Person.status == status)
        query = query.order_by(order)
        persons = query.paginate(page, limit, False).items

        result = []
        for person in persons:
            person.first_name = person.first_name if person.first_name else ''
            person.midle_name = person.midle_name if person.midle_name else ''
            person.last_name = person.last_name if person.last_name else ''
            name = "%s %s %s" % (
                person.last_name,
                person.first_name,
                person.midle_name
            )
            data = dict(
                id=person.id,
                name=name,
                card=person.card,
                status='active' if person.status == self.STATUS_VALID else '',
            )
            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )
        return value

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            self.payment_id = str(self.payment_id).rjust(20, '0')
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
