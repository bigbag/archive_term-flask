# -*- coding: utf-8 -*-
"""
    Консольное приложение для проверки лайков в соцсетях по базе жетонов

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask
from flask.ext.script import Command
from grab import Grab

from models.loyalty import Loyalty
from models.likes_stack import LikesStack
from models.soc_token import SocToken
from console.configs.payment import UnitellerConfig
from libs.facebook_api import FacebookApi


class CheckLikes(Command):

    def run(self):
        print "Start CheckSocial:"

        lStack = LikesStack.query.filter().all()

        for stackItem in lStack:
            userToken = SocToken.query.filter_by(
                id=stackItem.token_id).first()

            url = Loyalty.get_action_link(stackItem.loyalty_id)

            if len(url):
                socToken = SocToken.query.filter_by(
                    id=stackItem.token_id).first()
                pageLiked = FacebookApi.check_like(url, socToken.user_token)

                if pageLiked:
                    print 'You are liked this page: ' + url
                else:
                    print 'You are not liked this page: ' + url
                    
                #stackItem.delete()

        return True
