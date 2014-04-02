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
from models.loyalty import Loyalty
from models.person_event import PersonEvent
from models.likes_stack import LikesStack
from models.soc_token import SocToken
from console.configs.payment import UnitellerConfig
from libs.socnet.socnets_api import SocnetsApi


class CheckLikes(Command):

    def run(self):
        lStack = LikesStack.query.filter().all()

        for stackItem in lStack:
            url = Loyalty.get_action_link(stackItem.loyalty_id)
            action = Loyalty.query.get(stackItem.loyalty_id)

            if len(url):
                socToken = SocToken.query.get(stackItem.token_id)
                socApi = SocnetsApi()
                pageLiked = socApi.check_soc_sharing(
                    action.sharing_type, url, socToken.id, stackItem.loyalty_id)

                if pageLiked:
                    PersonEvent.add_by_user_loyalty_id(
                        socToken.user_id, stackItem.loyalty_id)
                    # print 'user complied with the conditions for ' + url
                    stackItem.delete()

                else:
                    print 'user not complied with the conditions for ' + url
        return True
