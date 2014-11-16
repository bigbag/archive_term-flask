# -*- coding: utf-8 -*-
"""
    Контролер для реализации внутреннего апи

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint, jsonify, request, make_response

from configs.yandex import YandexMoneyConfig
from yandex_money.api import Wallet

from decorators.header import *
from helpers.error_json_helper import *

from models.payment_card import PaymentCard
from models.payment_wallet import PaymentWallet

from web.tasks import payment

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
    except:
        pass
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

    payment.get_ym_token.send.delay(discodes_id, code)
    result['error'] = 0

    return make_response(jsonify(result))
