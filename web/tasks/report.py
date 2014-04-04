# -*- coding: utf-8 -*-
"""
    Задачи по формированию отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
import json
import xlsxwriter

from datetime import datetime, timedelta
from sqlalchemy.sql import func

from web import app, db
from web.celery import celery

from models.report import Report
from models.person import Person
from models.term import Term
from models.firm import Firm
from models.report_stack import ReportStack
from models.term_corp_wallet import TermCorpWallet

from web.tasks import mail
from web.emails.term.report import ReportMessage

from helpers import date_helper


@celery.task
def report_manager(interval):
    report_stack = ReportStack.query.filter_by(interval=interval).all()

    for key in report_stack:
        report_generate.delay(key)

    return True


@celery.task
def report_generate(report_stack):
    results = False
    attach = False

    if report_stack.type == ReportStack.TYPE_PERSON:
        if report_stack.interval != ReportStack.INTERVAL_ONCE:
            results = get_person_interval(report_stack)
            if report_stack.excel == ReportStack.EXCEL_YES:
                attach = get_person_interval_xls(results, report_stack.firm_id)

    if not results:
        return False

    if results['summ'] == 0:
        return False

    emails = json.loads(report_stack.emails)
    for email in emails:
        mail.send.delay(
            ReportMessage,
            to=email,
            attach=attach,
            results=results)

    return True


def get_person_query(interval, firm_id):
    query = db.session.query(
        Report.person_id,
        func.sum(Report.amount),
        Report.term_id,)

    query = query.filter(Report.corp_type == Report.CORP_TYPE_ON)
    query = query.filter(Report.person_firm_id == firm_id)
    query = query.filter(
        Report.creation_date.between(interval[0], interval[1]))

    query = query.group_by(Report.person_id, Report.term_id)
    query = query.order_by(Report.name)
    return query


def get_person_interval(report_stack):
    firm = Firm.query.get(report_stack.firm_id)
    if not firm:
        return False

    interval_meta = ReportStack().get_interval_meta(report_stack.interval)
    persons = Person().get_dict_by_firm_id(report_stack.firm_id)
    terms = Term().select_name_dict()
    corp_wallets = TermCorpWallet().get_dict_by_firm_id(
        report_stack.firm_id)

    yesterday = datetime.now() - timedelta(1)
    interval = date_helper.get_date_interval(yesterday, interval_meta)

    query = get_person_query(interval, report_stack.firm_id)
    reports = query.all()
    result = dict(
        data={},
        summ=0,
        persons=[],
        terms={},
        firm_name=firm.name
    )
    for row in reports:
        if row.person_id not in result['persons']:
            result['persons'].append(row.person_id)

        if row[0] not in result['data']:
            result['data'][row[0]] = {}
            result['data'][row[0]]['amount'] = 0

        if row[2] not in result['terms']:
            result['terms'][row[2]] = dict(name=terms[row[2]])
            result['terms'][row[2]]['amount'] = 0

        data = result['data'][row[0]]
        data['name'] = persons[row[0]]['name']
        data['tabel_id'] = persons[row[0]]['tabel_id']
        data['card'] = persons[row[0]]['card']

        if row[0] in corp_wallets:
            data['wallet_interval'] = corp_wallets[row[0]]['interval']
            data['wallet_limit'] = corp_wallets[row[0]]['limit'] / 100

        amount = row[1] / 100
        data['amount'] = data['amount'] + amount

        result['summ'] = result['summ'] + amount
        result['terms'][row[2]]['amount'] = result[
            'terms'][row[2]]['amount'] + amount

        if 'term' not in data:
            data['term'] = {}
        data['term'][row[2]] = row[1] / 100

        result['data'][row[0]] = data

    result['interval'] = '%s - %s' % (
        interval[0].strftime('%d.%m.%Y'),
        interval[1].strftime('%d.%m.%Y'))

    return result


def get_person_interval_xls(results, firm_id):
    data = results['data']
    persons = results['persons']
    terms = results['terms']

    file_name = "./tmp/report_%s_%s.xlsx" % (
        firm_id, int(time.time()))

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': 1})
    border = workbook.add_format({'border': 1})
    border_bold = workbook.add_format({'bold': 1, 'border': 1})

    keys = (
        'name',
        'tabel_id',
        'card',
        'wallet_interval',
        'wallet_limit',
        'amount')

    cols = dict(
        name=u'ФИО',
        tabel_id=u'Таб. номер',
        card=u'Номер карты',
        wallet_interval=u'Статус кошелька',
        wallet_limit=u'Размер кошелька, руб',
        amount=u'Итого'
    )
    worksheet.set_column(0, len(keys) + len(terms), 13)

    worksheet.write(1, 0, u'Отчет за период', bold)
    worksheet.write(1, 1, results['interval'], bold)

    row = 3
    col = 0
    for key in keys:
        worksheet.write(row, col, cols[key], border_bold)
        col += 1

    row = 4
    for person in persons:
        if person not in data:
            continue

        col = 0
        for key in keys:
            worksheet.write(row, col, data[person][key], border)
            col += 1

        row += 1

    worksheet.write(row, 0, u'Итого', bold)
    worksheet.write(row, 5, results['summ'], bold)

    col = len(cols)
    for key in terms:
        worksheet.write(3, col, terms[key]['name'], border_bold)
        worksheet.write(row, col, terms[key]['amount'], bold)

        row = 4
        for person in persons:
            if person not in data:
                continue

            if key not in data[person]['term']:
                worksheet.write(row, col, 0, border)
            else:
                worksheet.write(
                    row,
                    col,
                    data[person]['term'][key],
                    border)
            row += 1

        col += 1
    return file_name
