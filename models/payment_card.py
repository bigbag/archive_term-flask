# -*- coding: utf-8 -*-
"""
    Модель для привязанных карт


    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import db, app

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi

from models.base_model import BaseModel
from models.payment_history import PaymentHistory
from models.payment_wallet import PaymentWallet
from models.user import User


class PaymentCard(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'payment_card'

    STATUS_PAYMENT = 1
    STATUS_ARCHIV = 0

    MAX_LINKING_CARD_TIMEOUT = 60 * 60

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship('User')
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    wallet = db.relationship('PaymentWallet')
    pan = db.Column(db.String(128), nullable=False)
    token = db.Column(db.Text(), nullable=False)
    type = db.Column(db.String(128), nullable=False, index=True)
    status = db.Column(db.Integer(), nullable=False, index=True)

    def get_linking_params(self, order_id=0, url=None):
        """Запрос параметров для привязки карты"""

        ym = YaMoneyApi(YandexMoneyConfig)
        payment = ym.get_request_payment_to_shop(
            1, ym.const.CARD_PATTERN_ID, order_id)
        if not payment:
            return False

        if not 'request_id' in payment:
            app.logger.error(
                'Linking card: yandex api error - %s' %
                payment['error'])
            return False

        if url:
            ym.success_uri = url
            ym.fail_uri = url

        status = ym.get_process_external_payment(payment['request_id'])
        if not 'status' in status:
            app.logger.error('Linking card: Not found field status')
            return False

        if status['status'] != 'ext_auth_required':
            return False

        if not 'acs_uri' in status or not 'acs_params' in status:
            app.logger.error(
                'Linking card: Not found fields acs_uri or acs_params')
            return False

        result = dict(
            url=status['acs_uri'],
            params=status['acs_params']
        )

        return result

    def linking_init(self, discodes_id, url=None):
        """Инициализируем привязку карты"""

        wallet = PaymentWallet.query.filter(
            PaymentWallet.discodes_id == discodes_id).filter(
                PaymentWallet.user_id != 0).first(
        )
        if not wallet:
            return False

        history = PaymentHistory()
        history.add_linking_record(wallet.user_id, wallet.id)
        if not history.save():
            return False

        status = self.get_linking_params(history.id, url)
        if not status:
            history.delete()
            app.logger.error('Linking card: Fail in getting parameters')
            return False

        history.request_id = status['params']['cps_context_id']
        if not history.save():
            return False

        fail_history = PaymentHistory.get_fail_linking_record(
            history.id, history.wallet_id)
        for row in fail_history:
            db.session.delete(row)
        db.session.commit()

        return status

    def linking_card(self, history_id):
        """Привязываем карту, получаем платежный токен"""

        history = PaymentHistory.query.get(history_id)
        if not history:
            return False

        if history.status == PaymentHistory.STATUS_COMPLETE:
            return False

        wallet = PaymentWallet.query.get(history.wallet_id)
        if not wallet:
            return False

        ym = YaMoneyApi(YandexMoneyConfig)
        result = ym.get_process_external_payment(history.request_id)
        if not result or not 'status' in result:
            app.logger.error(
                'Linking card: Not found status field, request_id=%s' %
                history.request_id)
            return False

        if result['status'] == 'in_progress':
            history.status = PaymentHistory.STATUS_IN_PROGRESS
            if not history.save():
                return False
            return False
        elif result['status'] == 'refused':
            history.status = PaymentHistory.STATUS_FAILURE
            if not history.save():
                return False
            return False

        if result['status'] != 'success':
            return False

        self.set_archiv(history.wallet_id)

        card = self.add_payment(history, result)
        if not card:
            return False

        history.invoice_id = result['invoice_id']
        history.status = PaymentHistory.STATUS_COMPLETE
        if not history.save():
            return False

        if not card.save():
            return False

        wallet.blacklist = PaymentWallet.ACTIVE_ON
        wallet.save()

        return result

    def set_archiv(self, wallet_id):
        """Переводим ввсе карты привязанные к кошельку в архивное состояние"""

        old_cards = PaymentCard.query.filter_by(
            wallet_id=wallet_id,
            status=PaymentCard.STATUS_PAYMENT).all()

        for row in old_cards:
            row.status = PaymentCard.STATUS_ARCHIV
            db.session.add(row)
        db.session.commit()

        return True

    def add_payment(self, history, status):
        """ Добавляем платежную карту"""

        card = PaymentCard()
        card.user_id = history.user_id
        card.wallet_id = history.wallet_id

        if not 'money_source' in status:
            app.logger.error('Linking card: Not found card parameters')
            return False
        if not 'pan_fragment' in status['money_source'] or not 'payment_card_type' in status['money_source']:
            app.logger.error('Linking card: Not found card parameters')
            return False

        card.token = status['money_source']['money_source_token']
        card.pan = status['money_source']['pan_fragment']
        card.type = status['money_source']['payment_card_type']
        card.status = PaymentCard.STATUS_PAYMENT

        return card
