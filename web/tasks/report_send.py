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


class ReportSenderTask (object):

    def __init__(self):
        self.element = False
        self.result = False
        self.reports = False
        self.firm = False
        self.search_date = False
        self.type_meta = False

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
    def report_generate(element):
        if not element:
            return False

        sender_task = ReportSenderTask()
        sender_task.element = element

        sender_task.type_meta = element.get_type_meta()
        html_method_name = "_get_%s" % sender_task.type_meta
        excel_method_name = "_get_%s_xls" % sender_task.type_meta

        attibute = ReportSenderTask.__dict__
        if html_method_name not in attibute or excel_method_name not in attibute:
            return False

        sender_task.firm = Firm.query.get(element.firm_id)
        if not sender_task.firm:
            return False

        if element.interval == ReportStack.INTERVAL_ONCE:
        # and element.type == ReportStack.TYPE_PERSON:
            return False

        result = getattr(
            sender_task,
            html_method_name)()

        if not result:
            return False

        if result.all_summ == 0:
            return False

        if element.excel == ReportStack.EXCEL_YES:
            attach = getattr(sender_task, excel_method_name)(result)

        emails = json.loads(element.emails)
        for email in emails:
            mail.send.delay(
                ReportMessage,
                to=email,
                attach=attach,
                result=result,
                template=element.get_type_meta())

        element.launch_date = date_helper.get_curent_date()
        element.save()

        return True

    def _init_xls_file(self):
        if not self.firm:
            return False
        return "%s/excel%s_%s.xlsx" % (app.config['EXCEL_FOLDER'],
                                       self.firm.id, int(time.time()))

    def _init_result(self):
        if not self.element or not self.firm or not self.type_meta:
            return False

        interval_meta = ReportStack().get_interval_meta(self.element.interval)

        report = Report()
        report.firm_id = self.firm.id
        report.period = interval_meta

        self.search_date = datetime.now() - timedelta(1)
        interval = date_helper.get_date_interval(
            self.search_date, interval_meta)

        report_query_name = "%s_query" % self.type_meta
        if report_query_name not in Report.__dict__:
            return False
        self.reports = getattr(report, report_query_name)(interval).all()

        self.result = ReportSender()
        self.result.firm_id = self.firm.id
        self.result.firm_name = self.firm.name
        self.result.interval = report.format_search_date(self.search_date)

        self.result.interval_name = ReportStack().get_sender_interval_name(
            self.element.interval)
        self.result.type_name = ReportStack().get_sender_type_name(
            self.element.type)

        return True

    def _get_money(self):
        '''Формируем отчет по операциям с реальными деньгами'''

        self._init_result()
        result = self.result
        result.col_keys = ReportSender.get_money_keys()
        result.col_name = ReportSender.get_money_col_name()

        term_list = []
        for row in self.reports:
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

    def _get_money_xls(self, result):
        file_name = self._init_xls_file()
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
        worksheet.write(0, 0, result.firm_name, bold)
        worksheet.write(1, 0, result.type_name, bold)
        worksheet.write(2, 0, u'%s отчет' % result.interval_name, bold)
        worksheet.write(2, 1, result.interval, bold)

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
        worksheet.write(row, 1, result.all_count, bold)
        worksheet.write(row, 2, result.all_summ, bold)

        return file_name

    def _get_person(self):
        '''Формируем отчет за день, неделю, месяц по пользователям с корпоративными кошельками'''

        self._init_result()
        result = self.result
        result.col_keys = ReportSender.get_person_keys()
        result.col_name = ReportSender.get_person_col_name()

        persons = Person().get_dict_by_firm_id(self.firm.id)
        corp_wallets = TermCorpWallet().get_dict_by_firm_id(
            self.firm.id)

        for row in self.reports:
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

    def _get_person_xls(self, result):
        file_name = self._init_xls_file()
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
        worksheet.write(0, 0, result.firm_name, bold)
        worksheet.write(1, 0, result.type_name, bold)
        worksheet.write(2, 0, u'%s отчет' % result.interval_name, bold)
        worksheet.write(2, 1, result.interval, bold)

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
                worksheet.write(row, col, result.data[person][key], border)
                col += 1

            row += 1

        worksheet.write(row, 0, u'Итого', bold)
        worksheet.write(row, 5, result.all_summ, bold)

        col = len(result.col_name)
        # Блок с разбивкой расходов по терминалам
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

    def _get_term(self):
        '''Формируем отчет за день, неделю, месяц по терминалам'''
        return self._get_money()

    def _get_term_xls(self, result):
        return self._get_money_xls(result)
