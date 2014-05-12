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

from models.payment_wallet import PaymentWallet
from libs.socnet.socnets_api import SocnetsApi


@celery.task
def check_sharing():
    likes_stack = LikesStack.query.filter().all()

    if not len(likes_stack):
        return False

    for stack_item in likes_stack:
        url = PaymentLoyalty.get_action_link(stack_item.loyalty_id)
        if not len(url):
            continue

        action = PaymentLoyalty.query.get(stack_item.loyalty_id)
        if not action:
            continue

        soc_token = SocToken.query.get(stack_item.token_id)
        if not soc_token:
            continue

        page_liked = SocnetsApi().check_soc_sharing(
            action.sharing_type, url, soc_token.id, stack_item.loyalty_id)

        if not page_liked:
            continue

        user_wallets = PaymentWallet.query.filter_by(user_id=soc_token.user_id)
        wallet_list = []
        for wallet in user_wallets:
            wallet_list.append(wallet.id)

        query = WalletLoyalty.query
        query = query.filter(WalletLoyalty.wallet_id.in_(wallet_list))
        wallet_loyalties = query.filter_by(loyalty_id=action.id)

        for wl in wallet_loyalties:
            wl.checked = 1
            wl.save()

        PersonEvent.add_by_user_loyalty_id(
            soc_token.user_id, stack_item.loyalty_id)

        stack_item.delete()
    return True
