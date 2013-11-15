# -*- coding: utf-8 -*-
"""
    Модель событий для которых установлены
    таймауты обслуживания для каждого пользователя


    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import db, app


class PersonEvent(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'person_event'

    STATUS_ACTIVE = 1
    STATUS_BANNED = 0

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    person = db.relationship('Person')
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), index=True)
    term = db.relationship('Term')
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event')
    firm_id = db.Column(db.Integer, index=True)
    timeout = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, index=True)

    def __init__(self):
        self.timeout = 300
        self.status = self.STATUS_ACTIVE

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_valid_by_term_id(self, term_id):
        return self.query.filter_by(term_id=term_id, status=self.STATUS_ACTIVE).all()

    def get_by_person_id(self, person_id):
        return self.query.filter_by(person_id=person_id).all()

    def person_save(self, person):
        result = False

        persons_event = PersonEvent.query.filter_by(person_id=person.id)
        if persons_event:
            for person_event in persons_event:
                person_event.status = person.status
                db.session.add(person_event)

            db.session.commit()
            result = True
        else:
            result = True

        return result

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
