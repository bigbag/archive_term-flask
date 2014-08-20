# -*- coding: utf-8 -*-

"""
    Задачи по разбору отчетов с терминалов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
import os.path

from lxml import etree

from datetime import datetime, timedelta
from sqlalchemy.sql import func

from web import app
from web.celery import celery

from models.report import Report
from models.person import Person
from models.event import Event
from models.term import Term
from models.firm_term import FirmTerm

from helpers import date_helper

from web.tasks.report_send import ReportSenderTask


class ReportParserTask (object):

    @staticmethod
    @celery.task
    def report_manager(file_path):

        if not os.path.isfile(file_path):
            app.logger.error('File %s not found' % file_path)
            return False

        file_name = os.path.basename(file_path)
        params = ReportParserTask.parse_file_name(file_name)
        if not params:
            return False

        error = False
        result = ReportParserTask.parse_xml(file_path)

        for row in result:
            error = ReportParserTask.generate_report(params, row)

        if not error:
            new_file_patch = "%s/%s" % (
                app.config['ARCHIV_PATH'],
                params['date'])
            new_file_name = "%s/%s_%s" % (
                new_file_patch,
                params['term_id'],
                params['time'])
            if not os.path.exists(new_file_patch):
                os.makedirs(new_file_patch)
            os.rename(file_path, new_file_name)
            return True

        return False

    @staticmethod
    def parse_file_name(file_name):

        data = file_name.split('_')
        if not len(data) == 3:
            app.logger.error('Invalid file name %s' % file_name)
            return False

        try:
            term_id = int(data[0])
        except Exception as e:
            app.logger.error(e)
            return False

        report_date = data[1]
        report_time = data[2]
        if len(report_date) != 6 or len(report_time) != 6:
            app.logger.error('Invalid time or date in file name')
            return False

        if not date_helper.validate_date(report_time, '%H%M%S'):
            app.logger.error('Invalid time format %s' % report_time)
            return False

        if not date_helper.validate_date(report_date, '%y%m%d'):
            app.logger.error('Invalid date format %s' % report_date)
            return False

        return dict(
            term_id=term_id,
            date=report_date,
            time=report_time
        )

    @staticmethod
    def parse_xml(file_path):

        result = []
        try:
            tree = etree.parse(file_path)
        except Exception as e:
            app.logger.error(e)
        else:
            event_nodes = tree.xpath('/Report/Event')
            for event_node in event_nodes:
                event_key = event_node.get('type')

                if not event_key:
                    continue

                payments = []
                card_nodes = tree.xpath(
                    '/Report/Event[@type="%s"]/Card' %
                    event_key)
                for row in card_nodes:
                    if not row.get('summ'):
                        continue

                    if not row.get('type'):
                        continue

                    payments.append(
                        dict(
                            card=str(row.text).rjust(20, '0'),
                            amount=int(row.get('summ')),
                            type=row.get('type'),
                            date_time="%s %s" % (
                                row.get('date'),
                                row.get('time')),
                        )
                    )

                result.append(
                    dict(
                        event_key=event_key,
                        payments=payments
                    )
                )

        return result

    @staticmethod
    def generate_report(params, data):
        error = False
        term = Term.query.filter_by(hard_id=params['term_id']).first()
        if not term:
            app.logger.error('Not found term %s' % params['term_id'])
            return False

        event = Event.get_by_key(data['event_key'])
        if not event:
            app.logger.error('Not found event %s' % data['event_key'])
            return False

        firm_terms = FirmTerm.query.filter_by(term_id=term.id).all()
        payments = data['payments']
        report_max_date = ''
        for payment in payments:
            report = Report()
            report.term_id = term.id
            report.event_id = event.id
            report.type = payment['type']
            report.payment_id = payment['card']
            report.amount = payment['amount'] * int(term.factor)

            real_person = None
            for row in firm_terms:
                report.term_firm_id = row.firm_id
                person = Person.query.filter(
                    Person.payment_id == report.payment_id).filter(
                        Person.firm_id == row.child_firm_id).first()
                if not person:
                    continue
                real_person = person

            if real_person:
                report.name = real_person.name
                report.person_id = real_person.id
                report.person_firm_id = real_person.firm_id

            date_pattern = '%Y-%m-%d %H:%M:%S'
            date_time_utc = date_helper.convert_date_to_utc(
                payment['date_time'],
                term.tz,
                date_pattern,
                date_pattern)
            report.creation_date = date_time_utc

            if report.creation_date > report_max_date:
                report_max_date = report.creation_date

            error = report.add_new()

        if not error:
            ReportSenderTask.lost_report_watcher.delay(firm_terms, report_max_date)

        return error
