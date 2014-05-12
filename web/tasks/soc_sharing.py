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

from configs.uniteller import UnitellerConfig
from libs.socnet.socnets_api import SocnetsApi


@celery.task
def check_sharing():
    lStack = LikesStack.query.filter().all()

    if not len(lStack):
        return False

    for stackItem in lStack:
        url = PaymentLoyalty.get_action_link(stackItem.loyalty_id)

        if not len(url):
            continue

        action = PaymentLoyalty.query.get(stackItem.loyalty_id)
        if not action:
            continue

        socToken = SocToken.query.get(stackItem.token_id)
        if not socToken:
            continue

        socApi = SocnetsApi()
        pageLiked = socApi.check_soc_sharing(
            action.sharing_type, url, socToken.id, stackItem.loyalty_id)

        if not pageLiked:
            continue

        userWallets = PaymentWallet.query.filter_by(user_id=socToken.user_id)
        walletList = []
        for wallet in userWallets:
            walletList.append(wallet.id)

        walletLoyalties = WalletLoyalty.query.filter(WalletLoyalty.wallet_id.in_(walletList)).filter_by(
            loyalty_id=action.id)

        for wl in walletLoyalties:
            wl.checked = 1
            wl.save()

        PersonEvent.add_by_user_loyalty_id(
            socToken.user_id, stackItem.loyalty_id)

        stackItem.delete()
    return True
