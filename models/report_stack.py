# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на генерацию отчета

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class ReportStack(db.Model, BaseModel):

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
