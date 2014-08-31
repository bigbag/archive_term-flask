# -*- coding: utf-8 -*-
"""
    Модель для очереди заявок на генерацию отчета

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json

from web import db

from models.base_model import BaseModel

from helpers import hash_helper


class ReportStack(db.Model, BaseModel):

    __bind_key__ = 'stack'
    __tablename__ = 'report_stack'

    LOCK_FREE = 0
    LOCK_SET = 1

    EXCEL_NO = 0
    EXCEL_YES = 1

    INTERVAL_ONCE = 0
    INTERVAL_DAY = 1
    INTERVAL_WEEK = 2
    INTERVAL_MONTH = 3

    TYPE_CORP = 0
    TYPE_TERM = 1
    TYPE_MONEY = 2
    TYPE_PERSON = 3

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    emails = db.Column(db.Text, nullable=False)
    excel = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, index=True, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text)
    launch_date = db.Column(db.DateTime)
    check_summ = db.Column(db.Text, nullable=False)
    lock = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.excel = self.EXCEL_YES
        self.type = self.TYPE_TERM
        self.interval = self.INTERVAL_DAY
        self.lock = self.LOCK_FREE

    def get_interval_list(self):
        return [
            {'id': self.INTERVAL_ONCE, 'name': u"Один раз"},
            {'id': self.INTERVAL_DAY, 'name': u"Ежедневно"},
            {'id': self.INTERVAL_WEEK, 'name': u"Еженедельно"},
            {'id': self.INTERVAL_MONTH, 'name': u"Ежемесячно"}
        ]

    def interval_meta(self):
        return {
            self.INTERVAL_ONCE: 'once',
            self.INTERVAL_DAY: 'day',
            self.INTERVAL_WEEK: 'week',
            self.INTERVAL_MONTH: 'month'
        }

    def get_interval_meta(self, interval):
        interval_meta = self.interval_meta()
        if interval in interval_meta:
            return interval_meta[interval]
        return False

    def get_sender_interval_list(self):
        return {
            self.INTERVAL_ONCE: u"Разовый",
            self.INTERVAL_DAY: u"Ежедневный",
            self.INTERVAL_WEEK: u"Еженедельный",
            self.INTERVAL_MONTH: u"Ежемесячный"
        }

    def get_sender_interval_name(self, interval):
        interval_name = self.get_sender_interval_list()
        if interval in interval_name:
            return interval_name[interval]
        return False

    def get_type_list(self):
        return [
            {'id': self.TYPE_CORP, 'name': u"По корп. кошелькам"},
            {'id': self.TYPE_TERM, 'name': u"По терминалам"},
            {'id': self.TYPE_MONEY, 'name': u"Личным расходам"},
            {'id': self.TYPE_PERSON, 'name': u"По людям"},
        ]

    def get_sender_type_list(self):
        return {
            self.TYPE_CORP: u"Корпоративный, кошельки",
            self.TYPE_TERM: u"Корпоративный, терминалы",
            self.TYPE_MONEY: u"Личные расходы",
            self.TYPE_PERSON: u"Корпоративный, люди",
        }

    def get_sender_type_name(self, type):
        type_name = self.get_sender_type_list()
        if type in type_name:
            return type_name[type]
        return False

    def type_meta(self):
        return {
            self.TYPE_CORP: 'corp',
            self.TYPE_TERM: 'term',
            self.TYPE_MONEY: 'money',
            self.TYPE_PERSON: 'person',
        }

    def get_type_meta(self, type):
        type_meta = self.type_meta()
        if type in type_meta:
            return type_meta[type]
        return False

    def get_excel_list(self):
        return [
            {'id': self.EXCEL_YES, 'name': u"Да"},
            {'id': self.EXCEL_NO, 'name': u"Нет"},
        ]

    def get_json(self):
        self.email = json.loads(self.email)
        self.recipients = json.loads(self.recipients)
        return self

    def select_list(self, firm_id, **kwargs):
        order = kwargs[
            'order'] if 'order' in kwargs else 'name asc'
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        query = ReportStack.query.filter(
            ReportStack.firm_id == firm_id).filter(
            ReportStack.interval != self.INTERVAL_ONCE)
        query = query.order_by(order)
        report_stacks = query.paginate(page, limit, False).items

        result = []
        for report_stack in report_stacks:
            data = dict(
                id=report_stack.id,
                name=report_stack.name,
                interval_name=self.get_sender_interval_name(
                    report_stack.interval),
                type_name=self.get_sender_type_name(report_stack.type),
                excel=report_stack.excel
            )
            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )
        return value

    def copy_new_from_old(self):
        fields = self.__dict__.keys()
        fields.remove('id')
        fields.remove('_sa_instance_state')
        fields.remove('launch_date')
        fields.remove('check_summ')

        stack = ReportStack()
        map(lambda field: setattr(stack, field, getattr(self, field)), fields)

        return stack

    def set_check_summ(self):
        data = [
            str(self.firm_id),
            str(self.emails),
            str(self.excel),
            str(self.type),
            str(self.interval)]

        data = '&'.join(data)
        return hash_helper.get_content_md5(data)

    def save(self):
        if not self.check_summ:
            self.check_summ = self.set_check_summ()

        if not self.name:
            self.name = 'empty'

        self.emails = self.encode_field(self.emails)

        if self.details:
            self.details = self.encode_field(self.details)
        return BaseModel.save(self)
