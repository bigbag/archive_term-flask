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

from models.report import Report
from models.event import Event
from models.term import Term
from models.person import Person
from models.term_corp_wallet import TermCorpWallet
from models.payment_wallet import PaymentWallet
from models.payment_lost import PaymentLost
from models.payment_history import PaymentHistory
from models.payment_reccurent import PaymentReccurent


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
            new_file_patch = "%s/%s" % (
                app.config['UPLOAD_FOLDER'],
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

                    term = Term().get_by_id(term_id)
                    if not term:
                        term = Term()
                        term.id = term_id

                    card_nodes = tree.xpath(
                        '/Report/Event[@type="%s"]/Card' %
                        event_key)

                    for card_node in card_nodes:

                        report = Report()
                        report.term = term
                        report.event_id = event.id
                        report = report.get_db_view(card_node)

                        old_report = Report().get_by_check_summ(
                            report.check_summ)
                        if old_report:
                            continue

                        if not int(report.type) == Report.TYPE_PAYMENT:
                            person = Person.query.get(report.person_id)
                            # Если человек имеет корпоративный кошелек, обновляем его баланс
                            if not person.type == Person.TYPE_WALLET:
                                continue

                            report.corp_type = Report.CORP_TYPE_ON

                            corp_wallet = TermCorpWallet.query.filter_by(
                                person_id=person.id).first()
                            if corp_wallet:
                                corp_wallet.balance = int(
                                    corp_wallet.balance) - int(
                                        report.amount)
                                corp_wallet.save()

                                # Блокируем возможность платежей через корпоративный кошелек
                                if corp_wallet.balance < PaymentWallet.BALANCE_MIN:
                                    person.wallet_status = Person.STATUS_BANNED
                                    person.save()

                        else:
                            # Если операция платежная, обновляем баланс личного кошелька
                            wallet = PaymentWallet().get_by_payment_id(
                                report.payment_id)
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

                        report.save()

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
            if int(reccurent.wallet.balance) > PaymentWallet.BALANCE_MIN:
                continue

            history = PaymentHistory().get_new_by_wallet_id(
                reccurent.wallet.id)
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
