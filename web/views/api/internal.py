# -*- coding: utf-8 -*-
"""
    Контролер для реализации внутреннего апи

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask import Blueprint, jsonify, request, make_response


from decorators.header import *
from helpers.error_json_helper import *

from models.payment_card import PaymentCard

mod = Blueprint('api_internal', __name__)


@mod.route('/yandex/linking/<int:discodes_id>', methods=['GET'])
@json_headers
def api_internal_yandex_linking(discodes_id):

    result = {'error': 1}
    url = None

    if 'url' in request.args:
        url = request.args['url']

    params = PaymentCard().linking_init(discodes_id, url)
    if params:
        result = params
        result['error'] = 0

    return make_response(jsonify(result))
