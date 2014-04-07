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
from models.report_sender import ReportSender
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
    result = False
    attach = False

    firm = Firm.query.get(report_stack.firm_id)
    if not firm:
        return False

    meta = report_stack.get_type_meta()
    html_method_name = "_get_%s_interval" % meta
    excel_method_name = "_get_%s_interval_xls" % meta

    if report_stack.interval == ReportStack.INTERVAL_ONCE:
        return False

    if report_stack.type == ReportStack.TYPE_PERSON:
        result = _get_person_interval(report_stack, firm)
        if report_stack.excel == ReportStack.EXCEL_YES:
            attach = _get_person_interval_xls(result)
    elif report_stack.type == ReportStack.TYPE_MONEY:
        result = _get_money(report_stack, firm)
        if report_stack.excel == ReportStack.EXCEL_YES:
            attach = _get_money_interval_xls(result)

    if not result:
        return False

    if result.all_summ == 0:
        return False

    emails = json.loads(report_stack.emails)
    for email in emails:
        mail.send.delay(
            ReportMessage,
            to=email,
            attach=attach,
            result=result,
            template=report_stack.get_type_meta())

    report_stack.launch_date = date_helper.get_curent_date()
    report_stack.save()

    return True


def _get_money(report_stack, firm):
    '''Формируем отчет по операциям с реальными деньгами'''

    interval_meta = ReportStack().get_interval_meta(report_stack.interval)

    report = Report()
    report.firm_id = report_stack.firm_id
    report.period = interval_meta

    search_date = datetime.now() - timedelta(1)
    interval = date_helper.get_date_interval(search_date, interval_meta)
    reports = report.person_money_query(interval).all()

    result = ReportSender()
    result.firm_id = firm.id
    result.firm_name = firm.name
    result.interval = report.format_search_date(search_date)
    result.interval_name = ReportStack().get_sender_interval_name(
        report_stack.interval)
    result.type_name = ReportStack().get_sender_type_name(
        report_stack.type)
    result.col_keys = ReportSender.get_money_keys()
    result.col_name = ReportSender.get_money_col_name()

    term_list = []
    for row in reports:
        result.set_terms(row[0])
        if row[0] not in term_list:
            term_list.append(row[0])

        amount = row[2] / 100
        term_name = result.terms[row[0]]['name']
        result.data[row[0]] = dict(
            term_name=term_name,
            amount=amount,
            count=row[1]
        )
        result.all_count += row[1]
        result.all_summ += amount
    result.terms = term_list

    return result


def _get_money_interval_xls(result):
    file_name = "%s/excel%s_%s.xlsx" % (app.config['EXCEL_FOLDER'],
                                        result.firm_id, int(time.time()))

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': 1})
    border = workbook.add_format({'border': 1})
    border_bold = workbook.add_format({'bold': 1, 'border': 1})

    worksheet.set_column(0, 1, 25)
    worksheet.set_column(1, len(result.col_keys), 13)

    worksheet.write(0, 0, result.firm_name, bold)
    worksheet.write(1, 0, result.type_name, bold)
    worksheet.write(2, 0, u'%s отчет' % result.interval_name, bold)
    worksheet.write(2, 1, result.interval, bold)

    row = 3
    col = 0
    for key in result.col_keys:
        worksheet.write(row, col, result.col_name[key], border_bold)
        col += 1

    row = 4
    for term in result.terms:
        col = 0
        for key in result.col_keys:
            worksheet.write(row, col, result.data[term][key], border)
            col += 1

        row += 1

    worksheet.write(row, 0, u'Итого', bold)
    worksheet.write(row, 1, result.all_count, bold)
    worksheet.write(row, 2, result.all_summ, bold)

    return file_name


def _get_person_interval(report_stack, firm):
    '''Формируем отчет за день, неделю, месяц по пользователям с корпоративными кошельками'''

    interval_meta = ReportStack().get_interval_meta(report_stack.interval)
    persons = Person().get_dict_by_firm_id(report_stack.firm_id)
    corp_wallets = TermCorpWallet().get_dict_by_firm_id(
        report_stack.firm_id)

    report = Report()
    report.firm_id = report_stack.firm_id
    report.period = interval_meta

    search_date = datetime.now() - timedelta(1)
    interval = date_helper.get_date_interval(search_date, interval_meta)
    reports = report.person_corp_query(interval).all()

    result = ReportSender()
    result.firm_id = firm.id
    result.firm_name = firm.name
    result.interval = report.format_search_date(search_date)
    result.interval_name = ReportStack().get_sender_interval_name(
        report_stack.interval)
    result.type_name = ReportStack().get_sender_type_name(
        report_stack.type)
    result.col_keys = ReportSender.get_person_keys()
    result.col_name = ReportSender.get_person_col_name()

    for row in reports:
        result.set_terms(row[2])
        if row.person_id not in result.persons:
            result.persons.append(row.person_id)

        if row[0] not in result.data:
            result.data[row[0]] = dict(
                amount=0,
                name=persons[row[0]]['name'],
                tabel_id=persons[row[0]]['tabel_id'],
                card=persons[row[0]]['card']
            )

        data = result.data[row[0]]
        if row[0] in corp_wallets:
            data['wallet_interval'] = corp_wallets[row[0]]['interval']
            data['wallet_limit'] = corp_wallets[row[0]]['limit'] / 100

        amount = row[1] / 100
        data['amount'] = data['amount'] + amount

        result.all_summ += amount
        result.terms[row[2]]['amount'] = result.terms[
            row[2]]['amount'] + amount

        if 'term' not in data:
            data['term'] = {}
        data['term'][row[2]] = row[1] / 100

        result.data[row[0]] = data

    return result


def _get_person_interval_xls(result):
    file_name = "%s/excel%s_%s.xlsx" % (app.config['EXCEL_FOLDER'],
                                        result.firm_id, int(time.time()))

    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': 1})
    border = workbook.add_format({'border': 1})
    border_bold = workbook.add_format({'bold': 1, 'border': 1})

    worksheet.set_column(0, 1, 20)
    worksheet.set_column(1, len(result.col_keys) + len(result.terms), 13)

    worksheet.write(0, 0, result.firm_name, bold)
    worksheet.write(1, 0, result.type_name, bold)
    worksheet.write(2, 0, u'%s отчет' % result.interval_name, bold)
    worksheet.write(2, 1, result.interval, bold)

    row = 3
    col = 0
    for key in result.col_keys:
        worksheet.write(row, col, result.col_name[key], border_bold)
        col += 1

    row = 4
    for person in result.persons:
        if person not in result.data:
            continue

        col = 0
        for key in result.col_keys:
            worksheet.write(row, col, result.data[person][key], border)
            col += 1

        row += 1

    worksheet.write(row, 0, u'Итого', bold)
    worksheet.write(row, 5, result.all_summ, bold)

    col = len(result.col_name)
    for key in result.terms:
        worksheet.write(3, col, result.terms[key]['name'], border_bold)
        worksheet.write(row, col, result.terms[key]['amount'], bold)

        row = 4
        for person in result.persons:
            if person not in result.data:
                continue

            if key not in result.data[person]['term']:
                worksheet.write(row, col, 0, border)
            else:
                worksheet.write(
                    row,
                    col,
                    result.data[person]['term'][key],
                    border)
            row += 1

        col += 1
    return file_name
