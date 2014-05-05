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
from configs.payment import UnitellerConfig
from libs.socnet.socnets_api import SocnetsApi


@celery.task
def check_sharing(MessageClass, **kwargs):
    likes_stack = LikesStack.query.filter().all()

    for stack_item in likes_stack:
        url = PaymentLoyalty.get_action_link(stack_item.loyalty_id)
        action = PaymentLoyalty.query.get(stack_item.loyalty_id)

        if not len(url):
            continue

        soc_token = SocToken.query.get(stack_item.token_id)
        soc_api = SocnetsApi()
        page_liked = soc_api.check_soc_sharing(
            action.sharing_type, url, soc_token.id, stack_item.loyalty_id)

        if not page_liked:
            continue

        PersonEvent.add_by_user_loyalty_id(soc_token.user_id, stack_item.loyalty_id)
        stack_item.delete()
