# -*- coding: utf-8 -*-
"""
    Задачи связанные с платежами

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import app

from web.celery import celery

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi

from helpers import date_helper

from models.payment_history import PaymentHistory
from models.payment_card import PaymentCard
from models.payment_wallet import PaymentWallet
from models.term import Term
from models.report import Report


class PaymentTask (object):

    @staticmethod
    @celery.task
    def payment_manager():
        reports = Report.query.filter_by(
            type=Report.TYPE_PAYMENT,
            status=Report.STATUS_NEW).all()

        if not reports:
            return False

        for report in reports:
            history = PaymentHistory.query.filter_by(
                report_id=report.id).first()
            if history:
                continue
            PaymentTask.background_payment.delay(report.id)

        history = PaymentHistory().get_new_payment()
        for key in history:
            PaymentTask.check_status.delay(key.id)

        return True

    @staticmethod
    @celery.task
    def check_status(history_id):
        history = PaymentHistory.query.get(history_id)
        if not history:
            app.logger.error(
                'Check: Not found history, history_id=%s' %
                history_id)
            return False

        wallet = PaymentWallet.query.get(history.wallet_id)
        if not wallet:
            app.logger.error(
                'Check: Not found wallet, wallet_id=%s' %
                wallet_id)
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        result = ym.get_process_external_payment(history.request_id)

        if result['status'] in ('refused', 'ext_auth_required'):
            app.logger.error('Check: Fail, status=%s' % result['status'])
            wallet.add_to_blacklist()
            history.delete()
            return False

        if result['status'] == 'in_progress':
            history.status = PaymentHistory.STATUS_IN_PROGRESS
            history.save()

        elif result['status'] == 'success':
            if not 'invoice_id' in result:
                app.logger.error(
                    'Check: Fail, not found invoice_id, history_id=%s' %
                    history_id)
                return False

            history.invoice_id = result['invoice_id']
            history.status = PaymentHistory.STATUS_COMPLETE
            history.save()

            report = Report.query.get(history.report_id)
            report.status = Report.STATUS_COMPLETE
            report.save()

            wallet.remove_from_blacklist()

        return True

    @staticmethod
    @celery.task
    def background_payment(report_id):
        """Проводим фоновый платеж"""

        status = False
        report = Report.query.get(report_id)
        if not report:
            app.logger.error(
                'Payment: Not found report with id %s' %
                report.id)
            return False

        wallet = PaymentWallet.query.filter_by(
            payment_id=report.payment_id).first()
        if not wallet:
            app.logger.error(
                'Payment: Not found wallet with pid %s' %
                report.payment_id)
            return False

        history = PaymentHistory.query.filter_by(report_id=report.id).first()
        if history:
            return False

        history = PaymentHistory().from_report(report, wallet)
        if not history:
            app.logger.error(
                'Payment: Fail in history add, report_id=%s' %
                report.id)
            return False

        card = PaymentCard.query.filter_by(
            wallet_id=wallet.id,
            status=PaymentCard.STATUS_PAYMENT).first(
            )
        if not card:
            history.delete()
            wallet.add_to_blacklist()
            return False

        term = Term.query.get(report.term_id)
        if not term:
            app.logger.error('Payment: Not found term %s' % report.term_id)

        amount = int(
            report.amount) / int(
                Term.DEFAULT_FACTOR) * int(
                    term.factor)

        ym = YaMoneyApi(YandexMoneyConfig)
        payment = ym.get_request_payment_to_shop(
            amount, ym.const.PAYMENT_PATTERN_ID)
        if not payment or not 'request_id' in payment:
            app.logger.error(
                'Payment: Fail in request payment, report_id %s' %
                report_id)
            wallet.add_to_blacklist()
            history.delete()
            return False

        result = ym.get_process_external_payment(
            payment['request_id'], card.token)
        if result['status'] not in ('success', 'in_progress'):
            app.logger.error(
                'Payment: Fail in process payment, report_id %s' %
                report_id)
            wallet.add_to_blacklist()
            history.delete()
            return False

        history.request_id = payment['request_id']
        history.save()
        return True

    @staticmethod
    @celery.task
    def check_linking_manager():
        all_history = PaymentHistory.query.filter_by(
            type=PaymentHistory.TYPE_SYSTEM,
            status=PaymentHistory.STATUS_NEW).all()

        for key in all_history:
            PaymentTask.check_linking.delay(key)

        return True

    @staticmethod
    @celery.task
    def check_linking(history):
        result = PaymentCard().linking_card(history.id)
        if not result:
            delta = date_helper.get_curent_date(
                format=False) - history.creation_date
            if delta.total_seconds() > PaymentCard.MAX_LINKING_CARD_TIMEOUT:
                history.delete()
                return True

        return True
