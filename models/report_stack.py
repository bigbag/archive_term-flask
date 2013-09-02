# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на генерацию отчета

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib

from web import db
from web import app


class ReportStack(db.Model):

    __bind_key__ = 'stack'
    __tablename__ = 'report_stack'

    LOCK_FREE = 0
    LOCK_SET = 1

    EXCEL_NO = 0
    EXCEL_YES = 1

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    person = db.Column(db.Text, nullable=False)
    firm_id = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Date, nullable=False)
    stop = db.Column(db.Date, nullable=False)
    excel = db.Column(db.Integer, nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    check_summ = db.Column(db.String(32), nullable=False)
    lock = db.Column(db.Integer, index=True, nullable=False)

    def __init__(self):
        self.lock = self.LOCK_FREE
        self.excel = self.EXCEL_NO

    def __repr__(self):
        return '<id %r>' % (self.id)

    def get_json(self):
        self.email = json.loads(self.email)
        self.recipients = json.loads(self.recipients)

        return self

    def get_check_summ(self):
        return hashlib.md5("%s%s%s%s%s%s" % (
            str(self.email),
            str(self.person),
            str(self.firm_id),
            str(self.start),
            str(self.stop),
            str(self.type_id))).hexdigest()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            if not self.check_summ:
                self.check_summ = self.get_check_summ()
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True
