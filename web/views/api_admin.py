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

from decorators.header import *
from helpers.date_helper import *
from helpers.hash_helper import *
from helpers.error_xml_helper import *

from models.spot import Spot
from models.payment_wallet import PaymentWallet


api_admin = Blueprint('api_admin', __name__)


@api_admin.route('/spot/<int:hard_id>', methods=['GET'])
@xml_headers
def get_config(hard_id):
    """Возвращает информацию о споте по его HID"""

    hard_id = int(hard_id)

    if not len(str(hard_id)) == 16:
        abort(404)

    wallet = PaymentWallet.query.filter_by(
        hard_id=hard_id).first()

    if not wallet:
        abort(404)

    spot = Spot.query.filter_by(
        discodes_id=wallet.discodes_id).first()

    info_xml = render_template(
        'api_admin/spot_info.xml',
        spot=spot,
        wallet=wallet,
    ).encode('cp1251')

    response = make_response(info_xml)

    return response


@api_admin.route('/spot/add', methods=['POST'])
@xml_headers
def add_spot():
    """Добавляем спот и связанный с ним кошелёк"""

    add_success = 0
    hid = request.form['hid']
    pids = request.form['pids']

    if not hid or not pids:
        abort(400)

    if not len(str(hid)) == 16 or not len(str(pids)) == 10:
        abort(400)

    hid = int(hid)
    pids = int(pids)

    wallet = PaymentWallet.query.filter_by(
        hard_id=hid).first()

    if wallet:
        spot = Spot.query.filter_by(
            discodes_id=wallet.discodes_id).first()

        if not spot:
            abort(500)
    else:
        wallet = PaymentWallet()
        spot = Spot.query.filter_by(
            status=Spot.STATUS_ACTIVATED).first()

        wallet.discodes_id = spot.discodes_id
        wallet.hard_id = hid
        wallet.payment_id = str(wallet.get_pid(pids)).rjust(20, '0')

        add_success = 1

    add_xml = render_template(
        'api_admin/add_info.xml',
        spot=spot,
        wallet=wallet,
        add_success=add_success,
    ).encode('cp1251')

    response = make_response(add_xml)

    return response
