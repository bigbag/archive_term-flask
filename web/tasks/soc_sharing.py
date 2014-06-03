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

from models.payment_wallet import PaymentWallet
from libs.socnet.socnets_api import SocnetsApi


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
        url = PaymentLoyalty.get_action_link(task.loyalty_id)
        if not len(url):
            return False

        action = PaymentLoyalty.query.get(task.loyalty_id)
        if not action:
            return False

        soc_token = SocToken.query.get(task.token_id)
        if not soc_token:
            return False

        page_liked = SocnetsApi().check_soc_sharing(
            action.sharing_type, url, soc_token.id, task.loyalty_id)

        user_wallets = PaymentWallet.query.filter_by(user_id=soc_token.user_id)
        wallet_list = []
        for wallet in user_wallets:
            wallet_list.append(wallet.id)

        query = WalletLoyalty.query
        query = query.filter(WalletLoyalty.wallet_id.in_(wallet_list))
        wallet_loyalties = query.filter_by(loyalty_id=action.id)

        for wl in wallet_loyalties:
            if page_liked:
                wl.checked = 1
            else:
                wl.checked = 0
            wl.save()

        PersonEvent.add_by_user_loyalty_id(
            soc_token.user_id, task.loyalty_id)

        task.delete()
        return True

    @staticmethod
    @celery.task
    def rechek_manager():
        element_keys = PaymentLoyalty.query.filter(
            PaymentLoyalty.control_value.__ne__(None)).all()
        if not element_keys:
            return False

        for key in element_keys:
            SocSharingTask.recheck_loyalty.delay(key)

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
