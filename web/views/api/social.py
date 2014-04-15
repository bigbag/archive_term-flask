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
from models.payment_loyalty import PaymentLoyalty
from models.person_event import PersonEvent
from models.person import Person
from models.payment_wallet import PaymentWallet
from models.wallet_loyalty import WalletLoyalty
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
    count = PaymentLoyalty.DEFAULT_COUNT
    if 'count' in request.args:
        try:
            count = int(request.args['count'])
        except Exception as e:
            abort(405)
        count = PaymentLoyalty.MAX_COUNT if count > PaymentLoyalty.MAX_COUNT else count

    offset = 0
    if 'offset' in request.args:
        try:
            offset = int(request.args['offset'])
        except Exception as e:
            abort(405)

    loyalties = PaymentLoyalty.query.filter().order_by(
        PaymentLoyalty.id)[offset:(offset + count)]

    info_xml = render_template(
        'api/social/loyalties_list.xml',
        loyalties=loyalties,
        count=count,
        offset=offset
    ).encode('cp1251')

    response = make_response(info_xml)

    return response


@mod.route('/loyalty/<int:loyalty_id>', methods=['GET'])
@xml_headers
def api_social_get_loyalty(loyalty_id):
    """Возвращает детализацию по акции"""
    api_admin_access(request)

    if not loyalty_id:
        abort(400)

    try:
        loyalty_id = int(loyalty_id)
    except Exception as e:
        abort(405)

    loyalty = PaymentLoyalty.query.get(loyalty_id)

    if not loyalty:
        abort(404)

    wl = WalletLoyalty.query.filter_by(
        loyalty_id=loyalty.id)

    walletList = []
    for part in wl:
        if part.wallet_id not in walletList:
            walletList.append(part.wallet_id)

    partWallets = PaymentWallet.query.filter(
        PaymentWallet.id.in_(walletList))

    spotList = []
    for partWallet in partWallets:
        if partWallet.discodes_id not in spotList:
            spotList.append(partWallet.discodes_id)

    spots = Spot.query.filter(Spot.discodes_id.in_(spotList))

    spotWallets = []
    for spot in spots:
        for partWallet in partWallets:
            if partWallet.discodes_id == spot.discodes_id:
                wallet = {}
                wallet['discodes_id'] = spot.discodes_id
                wallet['barcode'] = spot.barcode
                wallet['hard_id'] = partWallet.hard_id
                spotWallets.append(wallet)

    info_xml = render_template(
        'api/social/loyalty_info.xml',
        loyalty=loyalty,
        spots=spotWallets
    ).encode('cp1251')

    response = make_response(info_xml)

    return response


@mod.route('/spot/loyalty/<ean>', methods=['GET'])
@xml_headers
def api_social_spot_loyalty(ean=False):
    """Возвращает акции, в которых участвует спот по EAN"""

    api_admin_access(request)
    ean = str(ean)
    if not ean or not len(ean) == 13 or not ean.isdigit():
        abort(400)

    spot = Spot.query.filter_by(
        barcode=ean).first()
    if not spot:
        abort(404)

    wallet = PaymentWallet.query.filter_by(
        discodes_id=spot.discodes_id).first()

    if not wallet:
        abort(404)

    wl = WalletLoyalty.query.filter_by(
        wallet_id=wallet.id)

    loyaltyList = []
    for part in wl:
        if part.loyalty_id not in loyaltyList:
            loyaltyList.append(part.loyalty_id)

    offset = 0
    if 'offset' in request.args:
        try:
            offset = int(request.args['offset'])
        except Exception as e:
            abort(405)

    count = PaymentLoyalty.MAX_COUNT
    if 'count' in request.args:
        try:
            count = int(request.args['count'])
        except Exception as e:
            abort(405)

    loyalties = PaymentLoyalty.query.filter(PaymentLoyalty.id.in_(loyaltyList)).order_by(
    )[offset:(offset + count)]

    info_xml = render_template(
        'api/social/spot_loyalty.xml',
        spot=spot,
        loyalties=loyalties,
        count=count,
        offset=offset
    ).encode('cp1251')
    response = make_response(info_xml)

    return response
