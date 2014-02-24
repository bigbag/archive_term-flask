# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи по взаимодействию с соцсетями

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import json
from flask import Blueprint, abort, request, make_response, url_for, render_template

from web import app, cache

from decorators.header import *
from helpers.error_xml_helper import *
from helpers import date_helper, hash_helper

from models.term_user import TermUser
from models.loyalty import Loyalty
from models.person_event import PersonEvent
from models.person import Person
from models.payment_wallet import PaymentWallet
from models.soc_token import SocToken
from models.likes_stack import LikesStack
from models.spot import Spot

mod = Blueprint('api_social', __name__)


def api_admin_access(request):
    headers = request.headers

    if 'Key' not in headers or 'Sign' not in headers:
        abort(400)

    term_user = TermUser().get_by_api_key(headers['Key'])
    if not term_user:
        abort(403)

    true_sign = hash_helper.get_api_sign(
        str(term_user.api_secret),
        request.form)

    if not true_sign == headers['Sign']:
        abort(403)


@mod.route('/loyalty', methods=['GET'])
@xml_headers
def api_social_get_loyalties():
    """Возвращает список акций"""
    api_admin_access(request)
    loyalties = Loyalty.query.filter().all()

    info_xml = render_template(
        'api/social/loyalties_list.xml',
        loyalties=loyalties
    ).encode('cp1251')

    response = make_response(info_xml)

    return response


@mod.route('/loyalty/<int:loyalty_id>', methods=['GET'])
@xml_headers
def api_social_get_loyalty(loyalty_id):
    """Возвращает детализацию по акции"""
    api_admin_access(request)
    loyalty = Loyalty.query.get(loyalty_id)
    terms = json.loads(loyalty.terms_id)
    events = PersonEvent.query.filter_by(
        event_id=loyalty.event_id, firm_id=loyalty.firm_id)

    personList = []

    for event in events:
        if event.person_id not in personList:
            personList.append(event.person_id)

    persons = Person.query.filter(Person.id.in_(personList))

    paymentsList = []

    for person in persons:
        if person.payment_id not in persons:
            paymentsList.append(person.payment_id)

    wallets = PaymentWallet.query.filter(
        PaymentWallet.payment_id.in_(paymentsList))

    usersList = []
    for wallet in wallets:
        if wallet.user_id not in usersList:
            usersList.append(wallet.user_id)

    lStack = LikesStack.query.filter().all()

    tokensList = []

    for stackItem in lStack:
        if stackItem.token_id not in tokensList:
            tokensList.append(stackItem.token_id)

    tokens = SocToken.query.filter(SocToken.id.in_(tokensList))

    for token in tokens:
        if token.user_id not in usersList:
            usersList.append(token.user_id)

    partWallets = PaymentWallet.query.filter(
        PaymentWallet.user_id.in_(usersList))

    spotList = []
    for partWallet in partWallets:
        if partWallet.discodes_id not in spotList:
            spotList.append(partWallet.discodes_id)

    spots = Spot.query.filter(Spot.discodes_id.in_(spotList))

    info_xml = render_template(
        'api/social/loyalty_info.xml',
        loyalty=loyalty,
        spots=spots
    ).encode('cp1251')

    response = make_response(info_xml)

    return response
