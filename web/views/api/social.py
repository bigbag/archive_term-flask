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
from helpers import date_helper

from models.payment_loyalty import PaymentLoyalty
from models.person_event import PersonEvent
from models.person import Person
from models.payment_wallet import PaymentWallet
from models.wallet_loyalty import WalletLoyalty
from models.soc_token import SocToken
from models.likes_stack import LikesStack
from models.spot import Spot

from web.views.api import base


mod = Blueprint('api_social', __name__)


@mod.route('/loyalty', methods=['GET'])
@xml_headers
def api_social_get_loyalties():
    """Возвращает список акций"""

    base._api_access(request)

    count = base._get_request_count(request, PaymentLoyalty.DEFAULT_COUNT)
    offset = base._get_request_offset(request)

    query = PaymentLoyalty.query.order_by(PaymentLoyalty.id)
    loyalties = query.limit(count).offset(offset).all()

    info_xml = render_template(
        'api/social/loyalties_list.xml',
        loyalties=loyalties,
        count=count,
        offset=offset
    ).encode('utf8')

    return make_response(info_xml)


@mod.route('/loyalty/<int:loyalty_id>', methods=['GET'])
@xml_headers
def api_social_get_loyalty(loyalty_id):
    """Возвращает детализацию по акции"""

    base._api_access(request)

    loyalty = PaymentLoyalty.query.get(loyalty_id)
    if not loyalty:
        abort(404)

    wallet_list = []
    wallet_loyalty = WalletLoyalty.query.filter_by(loyalty_id=loyalty.id).all()

    for part in wallet_loyalty:
        if part.wallet_id in wallet_list:
            continue
        wallet_list.append(part.wallet_id)

    spot_ist = []
    part_wallets = PaymentWallet.query.filter(PaymentWallet.id.in_(wallet_list)).all()

    for part_wallet in part_wallets:
        if part_wallet.discodes_id in spot_ist:
            continue
        spot_ist.append(part_wallet.discodes_id)

    spots = Spot.query.filter(Spot.discodes_id.in_(spot_ist)).all()

    spot_wallets = []
    for spot in spots:
        for part_wallet in part_wallets:
            if part_wallet.discodes_id != spot.discodes_id:
                continue
            spot_wallets.append(dict(
                discodes_id=spot.discodes_id,
                barcode=spot.barcode,
                hard_id=part_wallet.hard_id
            ))

    info_xml = render_template(
        'api/social/loyalty_info.xml',
        loyalty=loyalty,
        spots=spot_wallets
    ).encode('utf8')

    return make_response(info_xml)


@mod.route('/loyalty/ean/<ean>', methods=['GET'])
@xml_headers
def api_social_spot_loyalty(ean):
    """Возвращает акции, в которых участвует спот по EAN"""

    base._api_access(request)

    ean = str(ean)
    if not len(ean) == 13 or not ean.isdigit():
        abort(400)

    spot = Spot.query.filter_by(barcode=ean).first()
    if not spot:
        abort(404)

    wallet = PaymentWallet.query.filter_by(discodes_id=spot.discodes_id).first()
    if not wallet:
        abort(404)

    if 'id' in request.args:
        # данные только по требуемой акции
        try:
            loyalty_id = int(request.args['id'])
        except Exception as e:
            abort(405)

        loyalty = PaymentLoyalty.query.get(loyalty_id)
        if not loyalty:
            abort(404)

        wallet_loyalty = WalletLoyalty.query.filter_by(
            loyalty_id=loyalty.id, wallet_id=wallet.id).all()
        if not wallet_loyalty:
            abort(404)

        if wallet_loyalty[0].checked:
            loyalties = [loyalty]

        abort(404)
    else:
        # по всем акциям спота
        wallet_loyalty = WalletLoyalty.query.filter_by(
            wallet_id=wallet.id).filter_by(checked=1).all()
        if not wallet_loyalty:
            abort(404)

        loyaltyList = []
        for part in wallet_loyalty:
            if part.loyalty_id in loyaltyList:
                continue
            loyaltyList.append(part.loyalty_id)

        count = base._get_request_count(request, PaymentLoyalty.DEFAULT_COUNT)
        offset = base._get_request_offset(request)

        query = PaymentLoyalty.query.filter(PaymentLoyalty.id.in_(loyaltyList))
        loyalties = query.limit(count).offset(offset).all()

    info_xml = render_template(
        'api/social/spot_loyalty.xml',
        spot=spot,
        loyalties=loyalties,
        count=count,
        offset=offset
    ).encode('utf8')

    return make_response(info_xml)
