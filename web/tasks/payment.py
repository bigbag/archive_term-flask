# -*- coding: utf-8 -*-
"""
    Задачи связанные с платежами

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import copy

from web import app

from web.celery import celery

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi

from helpers import date_helper

from models.payment_history import PaymentHistory
from models.payment_card import PaymentCard
from models.payment_wallet import PaymentWallet
from models.payment_fail import PaymentFail
from models.term import Term
from models.firm import Firm
from models.report import Report


class PaymentTask (object):

    @staticmethod
    def get_fail_algorithm():

        def condition_generator(interval, start_interval, start, count):
            condition = [dict(count=i + start, delta=i * interval + start_interval)
                         for i in xrange(1, 1 + count)]

            return dict(condition=condition, start=start + count)

        algorithm = [
            dict(count=3, interval=5 * 60),
            dict(count=2, interval=60 * 60),
            dict(count=30, interval=24 * 60 * 60),
            dict(count=5, interval=7 * 24 * 60 * 60,
                 start_interval=30 * 24 * 60 * 60),
        ]

        result = []
        start = 0
        start_interval = 5 * 60
        for row in algorithm:
            if 'start_interval' in row:
                start_interval = row['start_interval']

            condition = condition_generator(
                row['interval'], start_interval, start, row['count'])
            result += condition['condition']
            start = condition['start']

        result.sort(reverse=True)

        return result

    @staticmethod
    @celery.task
    def payment_manager():
        PaymentTask.new_payment_manager.delay()
        PaymentTask.fail_payment_manager.delay()

    @staticmethod
    @celery.task
    def fail_payment_manager():
        payments = PaymentFail.query.all()
        if not payments:
            return False

        algorithm = PaymentTask.get_fail_algorithm()
        for payment in payments:
            delta = date_helper.get_curent_utc() - payment.timestamp
            for row in algorithm:
                if payment.count != row['count']:
                    continue

                if delta < row['delta']:
                    continue

                PaymentFail.add_or_update(payment.report_id)
                PaymentTask.background_payment.delay(payment.report_id)

    @staticmethod
    @celery.task
    def new_payment_manager():
        reports = Report.get_new_payment()
        if not reports:
            return False

        for report in reports:
            history = PaymentHistory.query.filter_by(
                report_id=report.id).first()
            if history:
                continue

            # Start: Костыль на время перехода от кошельков с балансом
            wallet = PaymentWallet.get_valid_by_payment_id(report.payment_id)
            if wallet and int(wallet.balance) > 0:
                PaymentTask.background_old_payment.delay(report.id)
                continue
            # End
            PaymentTask.background_payment.delay(report.id)

        history = PaymentHistory.get_new_payment()
        for key in history:
            PaymentTask.check_status.delay(key.id)

        return True

    @staticmethod
    @celery.task
    def check_status(history_id):
        history = PaymentHistory.query.get(history_id)
        if not history:
            message = 'Check: Not found history, history_id=%s' % history_id
            app.logger.error(message)
            return message

        wallet = PaymentWallet.query.get(history.wallet_id)
        if not wallet:
            message = 'Check: Not found wallet, wallet_id=%s' % wallet_id
            app.logger.error(message)
            return message

        ym = YaMoneyApi(YandexMoneyConfig)
        result = ym.get_process_external_payment(history.request_id)

        if result['status'] in ('refused', 'ext_auth_required'):
            PaymentFail.add_or_update(report_id)
            wallet.add_to_blacklist()
            history.delete()

            message = 'Check: Fail, status=%s' % result['status']
            app.logger.error(message)
            return message

        if result['status'] == 'in_progress':
            history.status = PaymentHistory.STATUS_IN_PROGRESS
            history.save()

        elif result['status'] == 'success':
            if not 'invoice_id' in result:
                message = 'Check: Fail, not found invoice_id, history_id=%s' % history_id
                app.logger.error(message)
                return message

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

        report = Report.query.get(report_id)
        if not report:
            message = 'Payment: Not found report with id %s' % report.id
            app.logger.error(message)
            return message

        wallet = PaymentWallet.get_by_payment_id(report.payment_id)
        if not wallet:
            message = 'Payment: Not found wallet with pid %s' % report.payment_id
            app.logger.error(message)
            return message

        history = PaymentHistory.query.filter_by(report_id=report.id).first()
        if history:
            return False

        history = PaymentHistory().from_report(report, wallet)
        if not history:
            message = 'Payment: Fail in history add, report_id=%s' % report.id
            app.logger.error(message)
            return message

        card = PaymentCard.query.filter_by(
            wallet_id=wallet.id,
            status=PaymentCard.STATUS_PAYMENT).first(
            )
        if not card:
            PaymentFail.add_or_update(report_id)
            wallet.add_to_blacklist()
            history.delete()

            return False

        term = Term.query.get(report.term_id)
        if not term:
            app.logger.error('Payment: Not found term %s' % report.term_id)

        firm = Firm.query.get(report.term_firm_id)
        if not firm:
            app.logger.error(
                'Payment: Not found firm, with term %s' % report.term_id)

        amount = float(report.amount) / int(Term.DEFAULT_FACTOR)

        ym = YaMoneyApi(YandexMoneyConfig)
        payment = ym.get_request_payment_to_shop(
            amount, firm.pattern_id)
        if not payment or not 'request_id' in payment:
            PaymentFail.add_or_update(report_id)
            wallet.add_to_blacklist()
            history.delete()

            message = 'Payment: Fail in request payment, report_id %s, request %s' % (
                report_id, payment)
            app.logger.error(message)
            return message

        result = ym.get_process_external_payment(
            payment['request_id'], card.token)
        if result['status'] not in ('success', 'in_progress'):
            PaymentFail.add_or_update(report_id)
            wallet.add_to_blacklist()
            history.delete()

            message = 'Payment: Fail in request payment, report_id %s, request %s' % (
                report_id, result)
            app.logger.error(message)
            return message

        history.request_id = payment['request_id']
        history.save()
        return True

    # Start: Костыль на время перехода от кошельков с балансом
    @staticmethod
    @celery.task
    def background_old_payment(report_id):
        """Платеж с кошелька uniteller"""

        report = Report.query.get(report_id)
        if not report:
            message = 'Payment: Not found report with id %s' % report.id
            app.logger.error(message)
            return message

        wallet = PaymentWallet.get_valid_by_payment_id(report.payment_id)
        if not wallet:
            message = 'Payment: Not found wallet with pid %s' % report.payment_id
            app.logger.error(message)
            return message

        history = PaymentHistory.query.filter_by(report_id=report.id).first()
        if history:
            return False

        history = PaymentHistory().from_report(report, wallet)
        if not history:
            message = 'Payment: Fail in history add, report_id=%s' % report.id
            app.logger.error(message)
            return message

        term = Term.query.get(report.term_id)
        if not term:
            app.logger.error('Payment: Not found term %s' % report.term_id)

        new_balance = wallet.balance - report.amount

        if new_balance < 0:
            history.amount = wallet.balance
            wallet.balance = 0
            report.copy_new_from_old(new_balance)
        else:
            wallet.balance = new_balance

        if not wallet.save():
            return False

        history.request_id = 'old'
        history.status = PaymentHistory.STATUS_COMPLETE
        if not history.save():
            return False

        report.status = Report.STATUS_COMPLETE
        if not report.save():
            return False

        return True
    # End

    @staticmethod
    @celery.task
    def check_linking_manager():
        select_status = (
            PaymentHistory.STATUS_NEW,
            PaymentHistory.STATUS_IN_PROGRESS)

        all_history = PaymentHistory.query.filter(
            PaymentHistory.type == PaymentHistory.TYPE_SYSTEM).filter(
                PaymentHistory.status.in_(select_status)).all()

        for key in all_history:
            PaymentTask.check_linking.delay(key)

        return True

    @staticmethod
    @celery.task
    def check_linking(history):
        result = PaymentCard().linking_card(history.id)
        return result
