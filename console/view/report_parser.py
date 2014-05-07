# -*- coding: utf-8 -*-
"""
    Консольное приложение для генерации отчетов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
import time
from multiprocessing.dummy import Pool as ThreadPool
from lxml import etree
from flask import Flask, render_template
from flask.ext.script import Command

from console import app

from models.report import Report
from models.event import Event
from models.term import Term

from models.payment_reccurent import PaymentReccurent

from helpers import date_helper


class ReportParser(Command):

    "Report parser"

    def get_files(self):
        files_all = os.listdir(app.config['TMP_PACH'])
        report_files = []

        for report_file in files_all:
            data = report_file.split('_')
            if not len(data) == 3:
                continue

            try:
                term_id = int(data[0])
            except Exception as e:
                app.logger.error(e)
                return False

            report_date = data[1]
            report_time = data[2]

            if len(report_date) != 6 or len(report_time) != 6:
                continue

            if not date_helper.validate_date(report_time, '%H%M%S'):
                continue

            if not date_helper.validate_date(report_date, '%y%m%d'):
                continue

            result = dict(
                term_id=term_id,
                report_date=report_date,
                report_time=report_time)

            report_files.append(result)

        return report_files

    def report_parser(self, report_file):
        error = False
        term_id = report_file['term_id']
        report_time = report_file['report_time']
        report_date = report_file['report_date']

        file_name = "%s/%s_%s_%s" % (
            app.config['TMP_PACH'],
            term_id,
            report_date,
            report_time)
        new_file_patch = "%s/%s" % (
            app.config['ARCHIV_PATH'],
            report_date)
        new_file_name = "%s/%s_%s" % (
            new_file_patch,
            term_id,
            report_time)

        try:
            tree = etree.parse(file_name)
        except Exception as e:
            app.logger.error(e)
        else:
            event_nodes = tree.xpath('/Report/Event')
            for event_node in event_nodes:
                event_key = event_node.get('type')

                if not event_key:
                    continue

                event = Event().get_by_key(event_key)
                if not event:
                    continue

                term = Term().get_by_hard_id(term_id)
                if not term:
                    term = Term()
                    term.hard_id = term_id

                card_nodes = tree.xpath(
                    '/Report/Event[@type="%s"]/Card' %
                    event_key)

                for card_node in card_nodes:
                    report = Report()
                    report.term = term
                    report.event_id = event.id
                    error = report.add_from_xml(card_node)

        if not error:
            if not os.path.exists(new_file_patch):
                os.makedirs(new_file_patch)

            os.rename(file_name, new_file_name)
            return True

        return False

    def run(self):
        try:
            report_files = self.get_files()
            if len(report_files) > 0:
                pool = ThreadPool(4)
                results = pool.map(self.report_parser, report_files)
                pool.close()
                pool.join()

            PaymentReccurent().set_reccurent_on()
        except Exception as e:
            app.logger.error(e)
