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
from models.payment_wallet import PaymentWallet
from models.person import Person
from models.person_event import PersonEvent
from models.likes_stack import LikesStack
from models.soc_token import SocToken
from console.configs.payment import UnitellerConfig
from libs.socnets_api import SocnetsApi


class CheckLikes(Command):

    def run(self):
        lStack = LikesStack.query.filter().all()

        for stackItem in lStack:
            userToken = SocToken.query.filter_by(
                id=stackItem.token_id).first()

            url = Loyalty.get_action_link(stackItem.loyalty_id)

            if len(url):
                socToken = SocToken.query.filter_by(
                    id=stackItem.token_id).first()
                pageLiked = SocnetsApi.check_like(
                    socToken.type, url, socToken.user_token)

                if pageLiked:
                    loyalty = Loyalty.query.filter_by(
                        id=stackItem.loyalty_id).first()
                    wallet = PaymentWallet.query.filter_by(
                        user_id=socToken.user_id).first()
                    if loyalty and wallet:
                        person = Person.query.filter_by(
                            firm_id=loyalty.firm_id, payment_id=wallet.payment_id).first()

                        if not person:
                            person = Person()
                            person.name = 'Участник промо-кампании'
                            person.firm_id = loyalty.firm_id
                            person.hard_id = wallet.hard_id
                            person.payment_id = wallet.payment_id
                            person.save()

                        terms = json.loads(loyalty.terms_id)
                        for term in terms:
                            event = PersonEvent.query.filter_by(
                                person_id=person.id, term_id=term, event_id=loyalty.event_id, firm_id=loyalty.firm_id).first()

                        if event:
                            if event.timeout > PersonEvent.LIKE_TIMEOUT:
                                event.status = PersonEvent.STATUS_BANNED
                                event.save()
                        else:
                            event = PersonEvent()
                            event.person_id = person.id
                            event.term_id = term
                            event.event_id = loyalty.event_id
                            event.firm_id = loyalty.firm_id
                            event.timeout = PersonEvent.LIKE_TIMEOUT
                            event.save()
                    # print 'user is liked this page: ' + url
                    stackItem.delete()

        return True
