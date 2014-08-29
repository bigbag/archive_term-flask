# -*- coding: utf-8 -*-
"""
    Задача проверки жетонов соцсетей по стеку

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import json
from grab import Grab

from web import app
from web.celery import celery

from models.payment_loyalty import PaymentLoyalty
from models.person_event import PersonEvent
from models.likes_stack import LikesStack
from models.soc_token import SocToken
from models.wallet_loyalty import WalletLoyalty
from models.payment_loyalty_sharing import PaymentLoyaltySharing

from models.payment_wallet import PaymentWallet
from libs.socnet.socnets_api import SocnetsApi
from libs.socnet.socnet_base import SocnetBase


class SocSharingTask (object):

    @staticmethod
    @celery.task
    def sharing_manager():
        element_keys = LikesStack.query.filter().all()
        if not element_keys:
            return False

        for key in element_keys:
            SocSharingTask.check_sharing.delay(key)

        return True

    @staticmethod
    @celery.task
    def check_sharing(task):
        condition = PaymentLoyaltySharing.query.get(task.sharing_id)
        if not condition:
            return False

        url = condition.link
        if not len(url):
            return False

        soc_token = SocToken.query.get(task.token_id)
        if not soc_token:
            return False

        page_liked = SocnetsApi().check_soc_sharing(
            condition.sharing_type, url, soc_token.id, task.sharing_id)

        if page_liked == SocnetBase.CONDITION_ERROR:
            return False

        user_wallets = PaymentWallet.query.filter_by(user_id=soc_token.user_id)
        wallet_list = []
        for wallet in user_wallets:
            wallet_list.append(wallet.id)

        query = WalletLoyalty.query
        query = query.filter(WalletLoyalty.wallet_id.in_(wallet_list))
        wallet_loyalties = query.filter_by(loyalty_id=condition.loyalty_id)

        for wl in wallet_loyalties:
            if page_liked == SocnetBase.CONDITION_PASSED:
                checked = []
                if wl.checked:
                    checked = json.loads(wl.checked)

                if condition.id not in checked:
                    checked.append(condition.id)
                    wl.checked = json.dumps(checked)

                if PaymentLoyaltySharing.query.filter_by(loyalty_id=wl.loyalty_id).count() <= len(checked):
                    wl.status = WalletLoyalty.STATUS_ON
                    PersonEvent.add_by_user_loyalty_id(
                        soc_token.user_id, condition.loyalty_id)

            elif page_liked == SocnetBase.CONDITION_FAILED and (wl.status == WalletLoyalty.STATUS_CONNECTING or wl.status == WalletLoyalty.STATUS_ERROR):
                wl.status = WalletLoyalty.STATUS_ERROR
                errors = []
                if wl.errors:
                    errors = json.loads(wl.errors)

                if condition.desc not in errors:
                    errors.append(condition.desc)
                    wl.errors = json.dumps(errors)

            elif page_liked == SocnetBase.CONDITION_FAILED and wl.status == WalletLoyalty.STATUS_ON:
                PersonEvent.delete_by_user_loyalty_id(
                    soc_token.user_id, condition.loyalty_id)

                wl.status = WalletLoyalty.STATUS_OFF
                wl.checked = '[]'
            wl.save()

        task.delete()
        return True

    @staticmethod
    @celery.task
    def rechek_manager():
        list = []
        loyalties = PaymentLoyalty.query.filter(
            PaymentLoyalty.stop_date > date_helper.get_curent_date()).all()

        for loyalty in loyalties:
            if loyalty.id in list:
                continue
            list.append(loyalty.id)

        element_keys = PaymentLoyaltySharing.query.filter(
            PaymentLoyaltySharing.control_value.__ne__(None), PaymentLoyaltySharing.loyalty_id.in_(list)).all()

        if not element_keys:
            return False

        for key in element_keys:
            SocSharingTask.recheck_condition.delay(key)

        return True

    @staticmethod
    @celery.task
    def recheck_loyalty(loyalty):
        control_value = SocnetsApi().get_control_value(loyalty.id)
        if control_value == loyalty.control_value:
            return False

        wallet_loyalties = WalletLoyalty.query.filter_by(
            loyalty_id=loyalty.id, checked=1).all()

        for wl in wallet_loyalties:
            wallet = PaymentWallet.query.filter_by(id=wl.wallet_id).first()
            if not wallet:
                continue

            token_type = SocnetsApi().get_token_type_by_sharing(
                loyalty.sharing_type)
            token = SocToken.query.filter_by(
                user_id=wallet.user_id, type=token_type).first()
            if not token:
                continue

            task_exists = LikesStack.query.filter_by(
                token_id=token.id, loyalty_id=loyalty.id).first()
            if task_exists:
                continue

            task = LikesStack()
            task.token_id = token.id
            task.loyalty_id = loyalty.id
            task.save()

        loyalty.control_value = control_value
        loyalty.save()

        return True

    @staticmethod
    @celery.task
    def recheck_condition(condition_id):
        condition = PaymentLoyaltySharing.query.get(condition_id)
        if not condition:
            return False

        control_value = SocnetsApi().get_control_value(condition_id)
        if control_value == condition.control_value:
            return False

        wallet_loyalties = WalletLoyalty.query.filter_by(
            loyalty_id=condition.loyalty_id, checked=1).all()

        for wl in wallet_loyalties:
            wallet = PaymentWallet.query.filter_by(id=wl.wallet_id).first()
            if not wallet:
                continue

            token_type = SocnetsApi().get_token_type_by_sharing(
                condition.sharing_type)
            token = SocToken.query.filter_by(
                user_id=wallet.user_id, type=token_type).first()
            if not token:
                continue

            task_exists = LikesStack.query.filter_by(
                token_id=token.id, sharing_id=condition.id).first()
            if task_exists:
                continue

            task = LikesStack()
            task.token_id = token.id
            task.sharing_id = condition.id
            task.save()

        condition.control_value = control_value
        condition.save()

        return True
