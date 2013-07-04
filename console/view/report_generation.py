# -*- coding: utf-8 -*-
"""
    Консольное приложение для генерации отчетов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
import time
from lxml import etree
from flask import Flask, render_template
from console import app
from flask.ext.script import Command
from web.models.report import Report
from web.models.event import Event
from web.models.term import Term
from web.models.firm_term import FirmTerm
from web.models.person import Person


class ReportGeneration(Command):

    "Report Generation"

    def run(self):
        files = os.listdir(app.config['UPLOAD_TMP'])
        for file in files:

            data = file.split('_')

            if not len(data) == 3:
                break

            term_id = data[0]
            report_date = data[1]
            report_time = data[2]

            file_name = app.config['UPLOAD_TMP'] + '/' + file
            new_file_patch = app.config['UPLOAD_FOLDER'] + '/' + report_date
            new_file_name = new_file_patch + '/' + term_id + '_' + report_time

            try:
                tree = etree.parse(file_name)
            except Exception as e:
                raise e
            else:
                event_nodes = tree.xpath('/Report/Event')
                for event_node in event_nodes:
                    event_type = event_node.get('type')

                    if not event_type:
                        break

                    event = Event.query.filter_by(key=event_type).first()
                    if not event:
                        break

                    term = Term.query.get(term_id)
                    if not term:
                        term = Term(term_id)

                    card_nodes = tree.xpath('/Report/Event/Card')
                    for card_node in card_nodes:

                        report = Report()
                        report.term = term
                        report.event_id = event.id
                        report = report.get_db_view(card_node)
                        check_summ = report.get_check_summ()

                        old_report = Report.query.filter_by(
                            check_summ=check_summ).first()

                        if int(report.type) == Report.TYPE_PAYMENT:
                            print "payment"

                        if not old_report:
                            report.save()

            if not os.path.exists(new_file_patch):
                os.makedirs(new_file_patch)

            # os.rename(file_name, new_file_name)

        # if not os.path.exists(file_patch):
        #     os.makedirs(file_patch)
        #
        #     report_datetime = str(report_datetime).split('_')
    # report_date = report_datetime[0]
    # report_time = report_datetime[1]
        # term = Term(21).get_term()
        # return files
