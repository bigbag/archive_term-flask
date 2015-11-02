# -*- coding: utf-8 -*-
"""
    Модель для сотрудников фирм

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
import xlrd
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from sqlalchemy.sql import func, outerjoin

from web import app, db, cache

from models.base_model import BaseModel

from helpers import date_helper


class Person(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'person'

    STATUS_VALID = 1
    STATUS_BANNED = 0

    TYPE_TIMEOUT = 0
    TYPE_WALLET = 1

    SCOPE_ACTIVE = 'active'
    SCOPE_BLOCKED = 'blocked'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    tabel_id = db.Column(db.String(150))
    birthday = db.Column(db.Date())
    firm_id = db.Column(db.Integer, db.ForeignKey('firm.id'))
    firm = db.relationship('Firm')
    card = db.Column(db.String(8))
    payment_id = db.Column(db.String(20), nullable=False, index=True)
    hard_id = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer, nullable=False, index=True)
    wallet_status = db.Column(db.Integer, nullable=False, index=True)
    type = db.Column(db.Integer, nullable=False, index=True)
    manually_blocked = db.Column(db.Integer)

    def __init__(self):
        self.status = self.STATUS_VALID
        self.wallet_status = self.STATUS_VALID
        self.type = self.TYPE_TIMEOUT
        self.creation_date = date_helper.get_current_date()
        self.name = u'Пользователь'
        self.manually_blocked = self.STATUS_VALID

    @staticmethod
    def get_dict_by_firm_id(firm_id):
        persons = Person.query.filter_by(firm_id=firm_id).all()

        result = {}
        for person in persons:
            result[person.id] = dict(
                name=person.name,
                tabel_id=person.tabel_id,
                card=person.card
            )

        return result

    @staticmethod
    def get_by_firm_id_search(firm_id, search, limit=5):
        query = Person.query.filter(Person.firm_id == firm_id)
        query = query.filter(Person.name.like('%' + search + '%'))
        persons = query.limit(limit).all()

        return list(dict(id=person.id, name=person.name) for person in persons)

    @staticmethod
    @cache.cached(timeout=30)
    def get_by_name(firm_id, name, limit):
        query = Person.query
        query = query.filter_by(firm_id=firm_id)
        query = query.filter(Person.name.like('%' + name + '%'))
        return query.limit(limit).all()

    @staticmethod
    @cache.cached(timeout=5)
    def select_list(firm_id, **kwargs):
        from models.person_event import PersonEvent

        order = kwargs[
            'order'] if 'order' in kwargs else 'name asc'
        order = "%s%s" % (order, ' desc' if 'order' in kwargs and 'order_desc' in kwargs and kwargs[
                          'order_desc'] else '')
        limit = kwargs['limit'] if 'limit' in kwargs else 10
        page = kwargs['page'] if 'page' in kwargs else 1

        search_request = kwargs[
            'request'] if 'request' in kwargs else False

        query = Person.query.filter(Person.firm_id == firm_id)

        if search_request:
            query = query.filter(
                Person.name.like('%' + search_request + '%') |
                Person.card.like('%' + search_request + '%'))

        if 'scope' in kwargs:
            if kwargs['scope'] == Person.SCOPE_ACTIVE:
                query = query.filter(
                    Person.manually_blocked == Person.STATUS_VALID)
                query = query.filter(
                    Person.wallet_status == Person.STATUS_VALID)

            elif kwargs['scope'] == Person.SCOPE_BLOCKED:
                query = query.filter(or_(
                    Person.manually_blocked == Person.STATUS_BANNED, Person.wallet_status == Person.STATUS_BANNED))

        query = query.outerjoin(
            PersonEvent, Person.id == PersonEvent.person_id)
        query = query.group_by(Person)
        query = query.add_columns(
            func.count(PersonEvent.id).label('event_count'))

        query = query.order_by(order)

        persons = query.paginate(page, limit, False).items

        result = []
        for item in persons:
            person = item[0]
            event_count = item[1]
            data = dict(
                id=person.id,
                name=person.name,
                card=person.card,
                wallet_status=int(person.wallet_status == Person.STATUS_VALID),
                status=person.status,
                event_count=event_count,
                hard_id=int(person.payment_id) if person.payment_id else 0,
                manually_blocked=person.manually_blocked,
            )
            result.append(data)

        value = dict(
            result=result,
            count=query.count(),
        )
        return value

    def person_remove(self):
        from models.term_corp_wallet import TermCorpWallet

        TermCorpWallet.query.filter_by(person_id=self.id).delete()
        self.delete()
        return True

    def get_status(self):
        from models.payment_wallet import PaymentWallet
        from models.person_event import PersonEvent
        from models.term_corp_wallet import TermCorpWallet

        if not self.payment_id:
            return self.STATUS_BANNED

        if self.manually_blocked == self.STATUS_BANNED:
            return self.STATUS_BANNED

        person_event = PersonEvent.query.filter(
            PersonEvent.person_id == self.id).first()

        if not person_event:
            return self.STATUS_BANNED

        corp_wallet = TermCorpWallet.query.filter(
            TermCorpWallet.person_id == self.id).first()

        if self.type == self.TYPE_WALLET and not corp_wallet:
            return self.STATUS_BANNED

        if self.type == self.TYPE_WALLET and corp_wallet.balance < TermCorpWallet.BALANCE_MIN:
            return self.STATUS_BANNED

        return self.STATUS_VALID

    @staticmethod
    def save_import_file(request):
        filepath = False
        file = request.files['ImportForm[file]']

        if not file or '.' not in file.filename:
            return filepath

        if file.filename.rsplit('.', 1)[1] in app.config['IMPORT_EXTENSIONS']:
            filepath = "%s/%s/%s" % (os.getcwd(), app.config['EXCEL_FOLDER'],
                                     secure_filename(file.filename))
            file.save(filepath)

        return filepath

    @staticmethod
    def excel_to_json_import(filepath):
        new_employers = []

        book = xlrd.open_workbook(filepath)
        sh = book.sheet_by_index(0)
        for i in range(sh.nrows):
            employer = {}

            if sh.cell(i, 0).ctype == 2:
                employer['name'] = sh.cell_value(i, 0)
            elif sh.cell(i, 0).ctype == 1:
                employer['name'] = unicode(sh.cell_value(i, 0))
            else:
                continue

            try:
                employer['card'] = unicode(
                    sh.cell_value(i, 1)).replace('.0', '')
            except Exception:
                pass
            try:
                employer['tabel_id'] = str(
                    sh.cell_value(i, 2)).replace('.0', '')
            except Exception:
                pass
            try:
                employer['code'] = str(sh.cell_value(i, 3))
            except Exception:
                pass

            employer['birthday'] = None
            new_employers.append(employer)

        return new_employers

    def save(self):
        self.status = self.get_status()
        return BaseModel.save(self)
