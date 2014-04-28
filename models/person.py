# -*- coding: utf-8 -*-
"""
    Модель для сотрудников фирм

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
import xlrd
from datetime import datetime
from werkzeug.utils import secure_filename

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

    def __init__(self):
        self.status = self.STATUS_VALID
        self.wallet_status = self.STATUS_VALID
        self.type = self.TYPE_TIMEOUT
        self.creation_date = date_helper.get_curent_date()
        self.name = u'Пользователь'

    @cache.cached(timeout=120, key_prefix='person_dict')
    def get_dict_by_firm_id(self, firm_id):
        persons = Person.query.filter_by(firm_id=firm_id).all()

        result = {}
        for person in persons:
            result[person.id] = dict(
                name=person.name,
                tabel_id=person.tabel_id,
                card=person.card
            )

        return result

    def select_list(self, firm_id, **kwargs):
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

    def person_remove(self):
        from models.term_corp_wallet import TermCorpWallet

        TermCorpWallet.query.filter_by(person_id=self.id).delete()
        self.delete()
        return True

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
                employer['card'] = unicode(sh.cell_value(i, 1)).replace('.0', '')
            except Exception:
                pass
            try:
                employer['tabel_id'] = str(sh.cell_value(i, 2)).replace('.0', '')
            except Exception:
                pass
            try:
                employer['code'] = str(sh.cell_value(i, 3))
            except Exception:
                pass

            employer['birthday'] = None
            new_employers.append(employer)

        return new_employers
