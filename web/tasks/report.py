# -*- coding: utf-8 -*-
"""
    Задачи по формированию отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from datetime import datetime, timedelta
from sqlalchemy.sql import func

from web import app, db
from web.celery import celery

from models.report import Report
from models.person import Person
from models.term import Term
from models.report_stack import ReportStack
from models.term_corp_wallet import TermCorpWallet

from helpers import date_helper


@celery.task
def report_manager(interval):
    report_stack = ReportStack.query.filter_by(interval=interval).all()

    for key in report_stack:
        report_generate.delay(key)

    return True


@celery.task
def report_generate(report_stack):

    if report_stack.type == ReportStack.TYPE_PERSON:
        if report_stack.interval != ReportStack.INTERVAL_ONCE:
            return report_person_interval(report_stack)

    return True


def report_person_query(interval, firm_id):
    query = db.session.query(
        Report.person_id,
        func.sum(Report.amount),
        Report.term_id,)

    query = query.filter(Report.corp_type == Report.CORP_TYPE_ON)
    query = query.filter(Report.person_firm_id == firm_id)
    query = query.filter(
        Report.creation_date.between(interval[0], interval[1]))

    query = query.group_by(Report.person_id, Report.term_id)
    query = query.order_by(Report.person_id)
    return query


def report_person_interval(report_stack):
    interval_meta = ReportStack().get_interval_meta(report_stack.interval)
    persons = Person().get_dict_by_firm_id(report_stack.firm_id)
    terms = Term().select_name_dict()
    corp_wallets = TermCorpWallet().get_dict_by_firm_id(
        report_stack.firm_id)

    yesterday = datetime.now() - timedelta(2)
    interval = date_helper.get_date_interval(yesterday, interval_meta)

    query = report_person_query(interval, report_stack.firm_id)
    reports = query.all()

    result = {}
    result['person'] = {}
    for row in reports:
        if row[0] not in result['person']:
            result['person'][row[0]] = {}
            result['person'][row[0]]['amount'] = 0

        data = result['person'][row[0]]
        data['name'] = persons[row[0]]['name']
        data['tabel_id'] = persons[row[0]]['tabel_id']
        data['card'] = persons[row[0]]['card']

        if row[0] in corp_wallets:
            corp_wallet = corp_wallets[row[0]]
            data['wallet_interval'] = corp_wallet['interval']
            data['wallet_limit'] = corp_wallet['limit'] / 100
        data['amount'] = data['amount'] + row[1] / 100

        if 'term' not in data:
            data['term'] = {}
        term_name = terms[row[2]]
        data['term'][term_name] = row[1] / 100

        result['person'][row[0]] = data

    return True
