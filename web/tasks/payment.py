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

    # TODO добавить отлов потеряных операций
    @staticmethod
    @celery.task
    def background_payment(report):
        """Проводим фоновый платеж"""

        status = False
        wallet = PaymentWallet.query.filter_by(
            payment_id=report.payment_id).first()
        if not wallet:
            app.logger.error(
                'Not found wallet with pid %s' %
                report.payment_id)
            return False

        history = PaymentHistory.query.filter_by(report_id=report.id).first()
        if history:
            return False

        history = PaymentHistory().from_report(report, wallet)

        if not history:
            app.logger.error('Fail in history add, report_id=%s' % report.id)
            return False

        card = PaymentCard.query.filter_by(
            wallet_id=wallet.id,
            status=PaymentCard.STATUS_PAYMENT).first(
            )
        if not card:
            wallet.add_to_blacklist()
            return False

        term = Term.query.get(report.term_id)
        if not term:
            app.logger.error('Not found term %s' % report.term_id)
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        amount = int(
            report.amount) / int(
                Term.DEFAULT_FACTOR) * int(
                    term.factor)
        status = ym.background_payment(amount, card.token)
        if not status:
            app.logger.error(
                'Fail in background payment, wallet %s' %
                wallet.id)
            wallet.add_to_blacklist()
            history.delete()
            return False

        history.request_id = status['request_id']
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
        history.status = PaymentHistory.STATUS_FAILURE
        history.save()

        result = PaymentCard().linking_card(history.request_id)
        if not result:
            delta = date_helper.get_curent_date(
                format=False) - history.creation_date
            if delta.total_seconds() > PaymentCard.MAX_LINKING_CARD_TIMEOUT:
                history.delete()
                return True

            history.status = PaymentHistory.STATUS_NEW
            history.save()

        return True

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
            PaymentTask.background_payment.delay(report)

        history = PaymentHistory.query.filter(
            PaymentHistory.report_id != 0).filter(
                PaymentHistory.invoice_id == 0).all(
                )

        for key in history:
            PaymentTask.check_status.delay(key.request_id)

        return True

    @staticmethod
    @celery.task
    def check_status(request_id):
        history = PaymentHistory.query.filter_by(request_id=request_id).first()
        if not history:
            app.logger.error('Not found history, request_id=%s' % report.id)
            return False

        wallet = PaymentWallet.query.get(history.wallet_id)
        if not wallet:
            app.logger.error('Not found wallet, wallet_id=%s' % wallet_id)
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        status = ym.get_payment_info(history.request_id)
        if not status:
            app.logger.error(
                'Fail in payment request_id=%s' %
                history.request_id)
            wallet.add_to_blacklist()
            history.delete()
            return False

        history.invoice_id = status['invoice_id']
        history.status = PaymentHistory.STATUS_COMPLETE
        history.save()

        report = Report.query.get(history.report_id)
        report.status = Report.STATUS_COMPLETE
        report.save()

        wallet.remove_from_blacklist()

        return True
