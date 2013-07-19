# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи администрирования

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os

from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
from web import app
from web import cache

from web.decorators.header import *
from web.helpers.date_helper import *
from web.helpers.hash_helper import *
from web.helpers.error_helper import *

from web.models.spot import Spot
from web.models.payment_wallet import PaymentWallet


api_admin = Blueprint('api_admin', __name__)


@api_admin.route('/spot/<int:discodes_id>', methods=['GET'])
@xml_headers
@cache.cached(timeout=120)
@md5_content_headers
def get_config(discodes_id):
    """Возвращает информацию о споте"""

    if not len(str(discodes_id)) == 6:
        abort(404)

    spot = Spot.query.filter_by(
        discodes_id=discodes_id).first()

    if not spot:
        abort(404)

    wallet = PaymentWallet.query.filter_by(
        discodes_id=discodes_id).first()

    info_xml = render_template(
        'api_admin/spot_info.xml',
        spot=spot,
        wallet=wallet,
    ).encode('cp1251')

    response = make_response(info_xml)

    return response
