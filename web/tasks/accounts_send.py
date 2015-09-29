# -*- coding: utf-8 -*-
"""
    Задача генерации счета

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""

import logging

from sqlalchemy.sql import func
from datetime import datetime, timedelta
from web import app
from web.celery import celery
from web.tasks import mail
from web.emails.term.account import AccountMessage

from helpers import date_helper

from models.payment_account import PaymentAccount
from models.firm import Firm
from models.firm_term import FirmTerm
from models.term import Term
from models.report import Report


class AccountSenderTask (object):

    @staticmethod
    @celery.task
    def accounts_manager():
        firms = Firm.query.filter(
            (Firm.transaction_percent > 0) | (Firm.transaction_comission > 0)).all()

        for firm in firms:
            AccountSenderTask.account_generate.delay(
                firm.id, datetime.utcnow())

    @staticmethod
    @celery.task
    def account_generate(firm_id, search_date, send=True):
        log = logging.getLogger('task')

        firm = Firm.query.get(firm_id)
        if not firm:
            log.error('Not found firm with id %s' % firm_id)
            return False

        firm_term = FirmTerm.get_list_by_firm_id(firm.id, False)
        leased_term = FirmTerm.get_list_by_firm_id(firm.id, True)
        comission_terms = []

        for term_id in (firm_term | leased_term):
            term = Term.query.get(term_id)
            if not term.has_comission:
                continue
            comission_terms.append(term.id)

        interval_date = search_date - timedelta(days=20)
        interval = date_helper.get_date_interval(interval_date, 'month')

        query = Report.query.filter(Report.term_firm_id == firm.id)
        query = query.filter(Report.status == Report.STATUS_COMPLETE)
        query = query.filter(Report.term_id.in_(comission_terms))
        query = query.filter(
            Report.creation_date.between(interval[0], interval[1]))
        reports = query.all()

        if not len(reports):
            log.debug('Empty report for firm id %s, date %s' %
                      (firm_id, search_date))
            return False

        query = PaymentAccount.query.filter(
            PaymentAccount.firm_id == firm.id)
        query = query.filter(
            PaymentAccount.status == PaymentAccount.STATUS_GENERATED)
        query = query.filter(func.DATE(
            PaymentAccount.generated_date) == func.DATE(search_date))

        account = query.first()
        if not account:
            account = PaymentAccount()
            account.firm_id = firm.id
            account.generated_date = search_date

        account.items_count = len(reports)
        account.summ = 0

        for report in reports:
            if firm.transaction_percent > 0:
                comission = float(report.amount) * \
                    (float(firm.transaction_percent) / 100 / 100)
                if firm.transaction_comission > 0 and comission < firm.transaction_comission:
                    comission = firm.transaction_comission

                account.summ = account.summ + comission
            elif firm.transaction_comission > 0:
                account.summ = account.summ + firm.transaction_comission

        account.items_count = len(reports)
        account.item_price = int(
            round(float(account.summ) / account.items_count))

        account.gprs_terms_count = 0

        if firm.gprs_rate:
            terms_used = 0
            gprs_summ = 0

            for term_id in firm_term:
                term = Term.query.get(term_id)
                delta = account.generated_date - term.config_date

                if not term.has_gprs:
                    continue

                if delta.total_seconds() > Term.USED_LAST_MONTH:
                    continue

                terms_used += 1
                gprs_summ += firm.gprs_rate

            if terms_used:
                account.gprs_terms_count = terms_used
                account.summ += gprs_summ

        account.filename = PaymentAccount.get_filename(firm_id, search_date)
        account.save()

        if not account.generate_pdf():
            log.error('Not generate account for firm id %s, date %s' %
                      (firm_id, search_date))
            account.delete()
            return False

        account.save()

        if not send:
            return True

        emails = firm.decode_field(firm.account_email)
        for email in emails:
            mail.send.delay(
                AccountMessage,
                to=email,
                attach='%s/%s' % (app.config['PDF_FOLDER'], account.filename),
                date_text=account.get_month_year())

        return True
