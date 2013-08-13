# -*- coding: utf-8 -*-
"""
    Модель событий доступных для привязки

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db


class Firm(db.Model):

    __bind_key__ = 'term'
    __tablename__ = 'firm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    inn = db.Column(db.String(300), index=True)
    sub_domain = db.Column(db.Text())
    logo = db.Column(db.Text())
    address = db.Column(db.Text())
    email = db.Column(db.Text())
    report_email = db.Column(db.Text(), nullable=False)
    report_excel = db.Column(db.Time, nullable=False)
    report_time = db.Column(db.Time, nullable=False)
    sending_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, id):
        self.id = id
        self.report_excel = {"day": 0, "month": 0, "singl": 0}
        self.report_time = "23:10:00"

    def get_json(self):
        self.report_email = json.loads(self.report_email)
        self.report_excel = json.loads(self.report_excel)
        self.report_time = json.loads(self.upload)

        return self

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
