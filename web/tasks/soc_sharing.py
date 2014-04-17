# -*- coding: utf-8 -*-
"""
    Задача проверки жетонов соцсетей по стеку

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from web.celery import celery
import json
from grab import Grab
from models.payment_loyalty import PaymentLoyalty
from models.person_event import PersonEvent
from models.likes_stack import LikesStack
from models.soc_token import SocToken
from console.configs.payment import UnitellerConfig
from libs.socnet.socnets_api import SocnetsApi


@celery.task
def check_sharing(MessageClass, **kwargs):
    lStack = LikesStack.query.filter().all()

    for stackItem in lStack:
        url = PaymentLoyalty.get_action_link(stackItem.loyalty_id)
        action = PaymentLoyalty.query.get(stackItem.loyalty_id)

        if len(url):
            socToken = SocToken.query.get(stackItem.token_id)
            socApi = SocnetsApi()
            pageLiked = socApi.check_soc_sharing(
                action.sharing_type, url, socToken.id, stackItem.loyalty_id)

            if pageLiked:
                PersonEvent.add_by_user_loyalty_id(
                    socToken.user_id, stackItem.loyalty_id)

                stackItem.delete()
