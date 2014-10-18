# -*- coding: utf-8 -*-
"""
    Задача проверки жетонов соцсетей по стеку

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import json
from web.celery import celery
from helpers import date_helper

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
        likes_stack = LikesStack.query.filter_by(
            lock=LikesStack.LOCK_FREE).all()
        if not likes_stack:
            return False

        active_stack = LikesStack.query.filter_by(
            lock=LikesStack.LOCK_SET).all()
        locked_loyalties = [task.wl_id for task in active_stack]

        for element in likes_stack:
            if element.wl_id in locked_loyalties:
                continue

            locked_loyalties.append(element.wl_id)
            element.lock = LikesStack.LOCK_SET
            element.save()

            SocSharingTask.check_sharing.delay(element.id)

        return True

    @staticmethod
    def remove_lock_and_exit(element):
        element.LikesStack.LOCK_FREE
        element.save()

        return False

    @staticmethod
    @celery.task
    def check_sharing(stack_id):
        likes_stack = LikesStack.query.get(stack_id)
        if not likes_stack:
            return False

        sharing_id = likes_stack.sharing_id
        condition = PaymentLoyaltySharing.query.get(sharing_id)
        if not condition:
            SocSharingTask.remove_lock_and_exit(likes_stack)

        url = condition.link
        soc_token = SocToken.query.get(likes_stack.token_id)
        if not soc_token:
            SocSharingTask.remove_lock_and_exit(likes_stack)

        page_liked = SocnetsApi.check_soc_sharing(
            condition.sharing_type, url, soc_token.id, sharing_id)

        if page_liked == SocnetBase.CONDITION_ERROR:
            SocSharingTask.remove_lock_and_exit(likes_stack)

        delete_task = True

        new_wallet = WalletLoyalty.query.with_lockmode(
            'update').get(likes_stack.wl_id)
        if page_liked == SocnetBase.CONDITION_PASSED:
            checked = []
            if new_wallet.checked:
                checked = new_wallet.decode_field(new_wallet.checked)

            if condition.id not in checked:
                checked.append(condition.id)

            new_wallet.checked = new_wallet.encode_field(checked)

            if not new_wallet.save():
                delete_task = False

            if PaymentLoyaltySharing.query.filter_by(loyalty_id=new_wallet.loyalty_id).count() <= len(checked):
                # подключение акции
                new_wallet.status = WalletLoyalty.STATUS_ON
                if not new_wallet.save():
                    delete_task = False
                if not PersonEvent.add_by_user_loyalty_id(
                        soc_token.user_id, condition.loyalty_id):
                    delete_task = False
            # else:
            #    SocSharingTask.sharing_manager.delay()

        elif page_liked == SocnetBase.CONDITION_FAILED and (new_wallet.status == WalletLoyalty.STATUS_CONNECTING or new_wallet.status == WalletLoyalty.STATUS_ERROR):
            new_wallet.status = WalletLoyalty.STATUS_ERROR
            errors = []
            if new_wallet.errors:
                errors = json.loads(new_wallet.errors)

            if condition.desc not in errors:
                errors.append(condition.desc)
                new_wallet.errors = json.dumps(errors)

            if not new_wallet.save():
                delete_task = False

        elif page_liked == SocnetBase.CONDITION_FAILED and new_wallet.status == WalletLoyalty.STATUS_ON:
            new_wallet.status = WalletLoyalty.STATUS_OFF
            new_wallet.checked = '[]'
            if not new_wallet.save():
                delete_task = False

            PersonEvent.delete_by_user_loyalty_id(
                soc_token.user_id, condition.loyalty_id)
        else:
            delete_task = False

        if not delete_task:
            SocSharingTask.remove_lock_and_exit(likes_stack)

        likes_stack.delete()

        return True

    @staticmethod
    @celery.task
    def rechek_manager():
        loyalties_list = []
        loyalties = PaymentLoyalty.query.filter(
            PaymentLoyalty.stop_date > date_helper.get_curent_date()).all()

        for loyalty in loyalties:
            if loyalty.id in loyalties_list:
                continue
            loyalties_list.append(loyalty.id)

        element_keys = PaymentLoyaltySharing.query.filter(
            PaymentLoyaltySharing.control_value.__ne__(None), PaymentLoyaltySharing.loyalty_id.in_(loyalties_list)).all()

        if not element_keys:
            return False

        for key in element_keys:
            SocSharingTask.recheck_condition.delay(key)

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
            loyalty_id=condition.loyalty_id, status=WalletLoyalty.STATUS_ON).all()

        for wallet in wallet_loyalties:
            wallet = PaymentWallet.query.filter_by(id=wallet.wallet_id).first()
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
