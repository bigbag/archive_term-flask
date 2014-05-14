# -*- coding: utf-8 -*-
"""
    Контролер для реализации внутреннего апи

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template

from web import app, cache

from decorators.header import *
from helpers.error_json_helper import *

from configs.yandex import YandexMoneyConfig
from libs.ya_money import YaMoneyApi

mod = Blueprint('api_internal', __name__)


@mod.route('/yandex/linking', methods=['GET'])
@json_headers
def api_internal_yandex_linking():

    ym = YaMoneyApi(YandexMoneyConfig)
    result = {'error': '1'}

    status = ym.linking_card()
    print status
    if status:
        result = status
        result['error'] = 0

    return make_response(jsonify(result))
