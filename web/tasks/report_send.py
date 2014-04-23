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
from models.report_result import ReportResult
from models.term_corp_wallet import TermCorpWallet

from web.tasks import mail
from web.emails.term.report import ReportMessage

from helpers import date_helper


class ReportSenderTask (object):

    @staticmethod
    @celery.task
    def report_manager(interval):
        element_keys = ReportStack.query.filter_by(interval=interval).all()
        if not element_keys:
            return False

        for key in element_keys:
            ReportSenderTask.report_generate.delay(key)

        return True

    @staticmethod
    @celery.task
    def report_generate(task):
        result = ReportResult(task)
        if not result.task:
            app.logger.error('Not found task')
            return False

        if not result.interval:
            app.logger.error('Faled interval')
            return False

        sender_task = ReportSenderTask()

        html_method_name = "_get_%s" % result.type['meta']
        excel_method_name = "_get_%s_xls" % result.type['meta']
        attibute = ReportSenderTask.__dict__
        if html_method_name not in attibute:
            return False
        if excel_method_name not in attibute:
            return False

        result = getattr(sender_task, "_get_%s" % result.type['meta'])(result)
        if result.data and result.all['summ'] != 0:

            if task.excel == ReportStack.EXCEL_YES:
                attach = getattr(
                    sender_task, "_get_%s_xls" %
                    result.type['meta'])(result)

            emails = task.decode_field(task.emails)
            for email in emails:
                mail.send.delay(
                    ReportMessage,
                    to=email,
                    attach=attach,
                    result=result,
                    template=result.type['meta'])

        if task.interval == ReportStack.INTERVAL_ONCE:
            task.delete()
        else:
            task.launch_date = date_helper.get_curent_date()
            task.save()

        return True

    def _get_money(self, result):
        '''Формируем отчет по операциям с реальными деньгами'''

        result.col_keys = ReportResult.get_money_keys()
        result.col_name = ReportResult.get_money_col_name()

        term_list = []
        for row in result.report:
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
            result.all['count'] += row[1]
            result.all['summ'] += amount
        result.terms = term_list

        return result

    def _get_money_xls(self, result):
        file_name = result.get_report_file()
        if not file_name:
            return False

        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': 1})
        border = workbook.add_format({'border': 1})
        border_bold = workbook.add_format({'bold': 1, 'border': 1})

        worksheet.set_column(0, 1, 25)
        worksheet.set_column(1, len(result.col_keys), 13)

        # Шапка таблицы
        worksheet.write(0, 0, result.firm.name, bold)
        worksheet.write(1, 0, result.type['templ_name'], bold)
        worksheet.write(
            2, 0, u'%s отчет' %
            result.interval['templ_name'], bold)
        worksheet.write(2, 1, result.interval['templ_interval'], bold)

        row = 3
        col = 0
        # Заголовки столбцов
        for key in result.col_keys:
            worksheet.write(row, col, result.col_name[key], border_bold)
            col += 1

        row = 4
        # Блок информации о оборотах с разбивкой по терминалам
        for term in result.terms:
            col = 0
            for key in result.col_keys:
                worksheet.write(row, col, result.data[term][key], border)
                col += 1

            row += 1

        worksheet.write(row, 0, u'Итого', bold)
        worksheet.write(row, 1, result.all['count'], bold)
        worksheet.write(row, 2, result.all['summ'], bold)

        return file_name

    def _get_corp(self, result):
        '''Формируем отчет по пользователям с корпоративными кошельками'''

        result.col_keys = ReportResult.get_corp_keys()
        result.col_name = ReportResult.get_corp_col_name()

        persons = Person().get_dict_by_firm_id(result.firm.id)
        corp_wallets = TermCorpWallet().get_dict_by_firm_id(
            result.firm.id)

        for row in result.report:
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

            result.all['summ'] += amount
            result.terms[row[2]]['amount'] = result.terms[
                row[2]]['amount'] + amount

            if 'term' not in data:
                data['term'] = {}
            data['term'][row[2]] = row[1] / 100

            result.data[row[0]] = data

        return result

    def _get_corp_xls(self, result):
        file_name = result.get_report_file()
        if not file_name:
            return False

        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({'bold': 1})
        border = workbook.add_format({'border': 1})
        border_bold = workbook.add_format({'bold': 1, 'border': 1})

        worksheet.set_column(0, 1, 20)
        worksheet.set_column(1, len(result.col_keys) + len(result.terms), 13)

        # Шапка таблицы
        worksheet.write(0, 0, result.firm.name, bold)
        worksheet.write(1, 0, result.type['templ_name'], bold)
        worksheet.write(
            2, 0, u'%s отчет' %
            result.interval['templ_name'], bold)
        worksheet.write(2, 1, result.interval['templ_interval'], bold)

        row = 3
        col = 0
        # Заголовоки столбцов
        for key in result.col_keys:
            worksheet.write(row, col, result.col_name[key], border_bold)
            col += 1

        row = 4
        # Блок суммарных расходов по сотрудникам
        for person in result.persons:
            if person not in result.data:
                continue

            col = 0
            for key in result.col_keys:
                key_data = 0
                if key in result.data[person]:
                    key_data = result.data[person][key]
                worksheet.write(row, col, key_data, border)
                col += 1

            row += 1

        result.all['summ']
        worksheet.write(row, 0, u'Итого', bold)
        worksheet.write(
            row,
            len(result.col_keys) - 1,
            result.all['summ'],
            bold)

        col = len(result.col_name)
        # Блок с разбивкой расходов по терминалам
        for key in result.terms:
            worksheet.write(3, col, result.terms[key]['name'], border_bold)
            worksheet.write(row, col, result.terms[key]['amount'], bold)

            row = 4
            for person in result.persons:
                if person not in result.data:
                    continue

                key_data = 0
                if key in result.data[person]['term']:
                    key_data = result.data[person]['term'][key]
                worksheet.write(row, col, key_data, border)
                row += 1

            col += 1
        return file_name

    def _get_person(self, result):
        '''Формируем отчет по всем пользователям из белого списка'''

        result.col_keys = ReportResult.get_person_keys()
        result.col_name = ReportResult.get_person_col_name()

        persons = Person().get_dict_by_firm_id(result.firm.id)

        for row in result.report:
            result.set_terms(row[2])
            if row.person_id not in result.persons:
                result.persons.append(row.person_id)

            if row[0] not in result.data:
                if row[0] in persons:
                    result.data[row[0]] = dict(
                        amount=0,
                        name=persons[row[0]]['name'],
                        tabel_id=persons[row[0]]['tabel_id'],
                        card=persons[row[0]]['card']
                    )
                else:
                    result.data[row[0]] = dict(
                        amount=0,
                        name=row[3],
                        tabel_id=0,
                        card=0
                    )

            data = result.data[row[0]]

            amount = row[1] / 100
            data['amount'] = data['amount'] + amount

            result.all['summ'] += amount
            result.terms[row[2]]['amount'] = result.terms[
                row[2]]['amount'] + amount

            if 'term' not in data:
                data['term'] = {}
            data['term'][row[2]] = row[1] / 100

            result.data[row[0]] = data

        return result

    def _get_person_xls(self, result):
        return self._get_corp_xls(result)

    def _get_term(self, result):
        '''Формируем отчет по терминалам'''
        return self._get_money(result)

    def _get_term_xls(self, result):
        return self._get_money_xls(result)
