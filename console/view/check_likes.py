# -*- coding: utf-8 -*-
"""
    Консольное приложение для проверки лайков в соцсетях по базе жетонов

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import json
from flask import Flask
from flask.ext.script import Command
from grab import Grab
from models.payment_loyalty import PaymentLoyalty
from models.person_event import PersonEvent
from models.likes_stack import LikesStack
from models.soc_token import SocToken
from configs.payment import UnitellerConfig
from libs.socnet.socnets_api import SocnetsApi


class CheckLikes(Command):

    def run(self):
        likes_stack = LikesStack.query.filter().all()
        for stack_item in likes_stack:
            url = PaymentLoyalty.get_action_link(stack_item.loyalty_id)
            action = PaymentLoyalty.query.get(stack_item.loyalty_id)

            if len(url):
                soc_token = SocToken.query.get(stack_item.token_id)
                soc_api = SocnetsApi()
                pageLiked = soc_api.check_soc_sharing(
                    action.sharing_type, url, soc_token.id, stack_item.loyalty_id)

                if pageLiked:
                    PersonEvent.add_by_user_loyalty_id(
                        soc_token.user_id, stack_item.loyalty_id)
                    # print 'user complied with the conditions for ' + url
                    stack_item.delete()

                else:
                    print 'user not complied with the conditions for ' + url
        return True
