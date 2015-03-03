# -*- coding: utf-8 -*-
"""
    Контролер для реализации внутреннего апи

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import logging
from flask import Blueprint, jsonify, request, make_response

from configs.yandex import YandexMoneyConfig
from yandex_money.api import Wallet

from decorators.header import *
from helpers.error_json_helper import *

from models.payment_card import PaymentCard
from models.payment_wallet import PaymentWallet
from models.spot import Spot
from models.spot_phone import SpotPhone

from web.tasks.payment import PaymentTask

mod = Blueprint('api_internal', __name__)


@mod.route('/yandex/linking/<int:discodes_id>', methods=['GET'])
@json_headers
def api_internal_yandex_linking(discodes_id):

    result = {'error': 1}
    if not PaymentWallet.get_valid_by_discodes_id(discodes_id):
        return make_response(jsonify(result))

    url = None
    if 'url' in request.args:
        url = request.args['url']

    params = PaymentCard().linking_init(discodes_id, url)
    if params:
        result = params
        result['error'] = 0

    return make_response(jsonify(result))


@mod.route('/yandex/get_auth_url/<int:discodes_id>', methods=['GET'])
@json_headers
def api_internal_yandex_get_auth_url(discodes_id):
    log = logging.getLogger('payment')

    result = {'error': 1}
    if not PaymentWallet.get_valid_by_discodes_id(discodes_id):
        return make_response(jsonify(result))

    url = None
    if 'url' in request.args:
        url = request.args['url']
    if not url:
        return make_response(jsonify(result))

    try:
        auth_url = Wallet.build_obtain_token_url(
            YandexMoneyConfig.CLIENT_ID,
            url,
            YandexMoneyConfig.WALLET_SCOPE)
    except Exception as e:
        log.error(e)
        return make_response(jsonify(result))
    else:
        result['error'] = 0
        result['url'] = auth_url

    return make_response(jsonify(result))


@mod.route('/yandex/get_token/<int:discodes_id>/<code>', methods=['GET'])
@json_headers
def api_internal_yandex_get_token(discodes_id, code):

    result = {'error': 1}
    if not PaymentWallet.get_valid_by_discodes_id(discodes_id):
        return make_response(jsonify(result))

    url = None
    if 'url' in request.args:
        url = request.args['url']
    if not url:
        return make_response(jsonify(result))

    PaymentTask.get_ym_token.delay(discodes_id, code, url)
    result['error'] = 0

    return make_response(jsonify(result))


@mod.route('/spot/transport_phone/<int:hard_id>/<code128>', methods=['GET'])
@json_headers
def api_internal_get_transport_phone(hard_id=False, code128=False):

    result = {'error': 1, 'phones': []}

    spot = Spot.query.filter(
        Spot.barcode == hard_id).filter(
        Spot.status.in_(Spot.VALID_STATUS)).first()

    if not spot:
        spot = Spot.query.filter(
            Spot.code128 == code128).filter(
                Spot.status.in_(Spot.VALID_STATUS)).first()

    if not spot:
        return make_response(jsonify(result))

    phones = SpotPhone.query.filter(
        SpotPhone.discodes_id == spot.discodes_id).filter(
            SpotPhone.school_sms == SpotPhone.SERVICE_ENABLED).all()

    for phone in phones:
        result['phones'].append(phone.phone)

    result['error'] = 0

    return make_response(jsonify(result))
