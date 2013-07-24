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
from flask.ext.script import Command

from console import app

from web.models.report import Report
from web.models.event import Event
from web.models.term import Term
from web.models.payment_wallet import PaymentWallet
from web.models.payment_lost import PaymentLost
from web.models.payment_history import PaymentHistory
from web.models.payment_reccurent import PaymentReccurent


class ReportParser(Command):

    "Report parser"

    def report_parser(self):
        files = os.listdir(app.config['UPLOAD_TMP'])
        for file in files:
            error = False
            data = file.split('_')

            if not len(data) == 3:
                continue

            term_id = data[0]
            report_date = data[1]
            report_time = data[2]

            file_name = app.config['UPLOAD_TMP'] + '/' + file
            new_file_patch = app.config['UPLOAD_FOLDER'] + '/' + report_date
            new_file_name = new_file_patch + '/' + term_id + '_' + report_time

            try:
                tree = etree.parse(file_name)
            except Exception as e:
                app.logger.error(e)
            else:
                event_nodes = tree.xpath('/Report/Event')
                for event_node in event_nodes:
                    event_type = event_node.get('type')

                    if not event_type:
                        continue

                    event = Event.query.filter_by(key=event_type).first()
                    if not event:
                        continue

                    term = Term.query.get(term_id)
                    if not term:
                        term = Term(term_id)

                    card_nodes = tree.xpath(
                        '/Report/Event[@type="%s"]/Card' %
                        event_type)

                    for card_node in card_nodes:

                        report = Report()
                        report.term = term
                        report.event_id = event.id
                        report = report.get_db_view(card_node)
                        check_summ = report.get_check_summ()

                        old_report = Report.query.filter_by(
                            check_summ=check_summ).first()

                        if old_report:
                            continue

                        report.save()

                        if not int(report.type) == Report.TYPE_PAYMENT:
                            continue

                        wallet = PaymentWallet.query.filter_by(
                            payment_id=report.payment_id).first()

                        if not wallet or wallet.user_id == 0:
                            lost = PaymentLost()
                            lost.add_lost_payment(report)
                        else:
                            wallet.balance = int(
                                wallet.balance) - int(
                                    report.amount)

                            if not wallet.save():
                                error = True
                                continue

                            history = PaymentHistory()
                            history.add_history(wallet, report)

            if not error:
                if not os.path.exists(new_file_patch):
                    os.makedirs(new_file_patch)

                os.rename(file_name, new_file_name)

                return True
            else:
                return False

    def set_reccurent_on(self):
        reccurents = PaymentReccurent.query.filter_by(
            status=PaymentReccurent.STATUS_OFF).all()

        for reccurent in reccurents:

            if not reccurent.wallet:
                continue
            if int(reccurent.wallet.balance) > 10100:
                continue

            history = PaymentHistory.query.filter_by(
                status=PaymentHistory.STATUS_NEW,
                wallet_id=reccurent.wallet.id,
            ).first()

            if history:
                continue

            reccurent.status = PaymentReccurent.STATUS_ON
            reccurent.save()

    def run(self):
        try:
            self.report_parser()
            self.set_reccurent_on()
        except Exception as e:
            app.logger.error(e)
