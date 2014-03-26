# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи администрирования

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os

from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
from web import app, cache

from decorators.header import *
from helpers.error_xml_helper import *

from helpers import hash_helper

from models.spot import Spot
from models.spot_dis import SpotDis
from models.payment_wallet import PaymentWallet
from models.payment_history import PaymentHistory
from models.term_user import TermUser


mod = Blueprint('api_admin', __name__)


def api_admin_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        headers = request.headers

        if 'Key' not in headers or 'Sign' not in headers:
            abort(400)

        term_user = TermUser().get_by_api_key(headers['Key']);
        if not term_user:
            abort(403)

        true_sign = hash_helper.get_api_sign(
            str(term_user.api_secret),
            request.form)

        if not true_sign == headers['Sign']:
            abort(403)

        return resp
    return decorated_function


@mod.route('/spot/generate', methods=['POST'])
@xml_headers
@api_admin_access
def api_admin_spot_generate():
    """Генерация спотов"""

    count = 10
    if 'count' in request.form:
        count = int(request.form['count'])
        count = 1 if count > Spot.MAX_GENERATE else count

    dis = SpotDis().get_new_list(count)
    if not dis:
        abort(405)

    result = {}
    for row in dis:
        if not row.set_generated():
            continue

        spot = Spot.query.get(row.id)
        if spot:
            continue
        spot = Spot()
        spot.discodes_id = row.id

        if not spot.save():
            if not row.set_init():
                continue

        result[spot.code] = spot.barcode

    return render_template(
        'api/admin/spot_list.xml',
        result=result,
    ).encode('cp1251')


@mod.route('/spot/linking', methods=['POST'])
@xml_headers
@api_admin_access
def api_admin_linking_spot():
    """Добавляем спот и связанный с ним кошелёк"""

    add_success = 0

    hid = request.form['hid']
    pids = request.form['pids']
    ean = request.form['ean']

    if not hid or not ean or not pids:
        abort(400)

    if not len(str(ean)) == 13:
        abort(400)

    hid = int(hid)
    pids = int(pids)

    spot = Spot.query.filter_by(
        barcode=ean).first()
    if not spot:
        abort(404)

    wallet = PaymentWallet.query.filter(
        (PaymentWallet.hard_id == hid) |
        (PaymentWallet.discodes_id == spot.discodes_id)).first()

    if not wallet:
        wallet = PaymentWallet()
        wallet.payment_id = wallet.get_pid(pids)
        wallet.hard_id = hid
        wallet.discodes_id = spot.discodes_id

        if wallet.save():
            spot.status = Spot.STATUS_ACTIVATED
            if not spot.save():
                abort(400)

            add_success = 1

    if wallet.discodes_id != spot.discodes_id:
        abort(400)

    return render_template(
        'api/admin/add_info.xml',
        spot=spot,
        wallet=wallet,
        add_success=add_success,
    ).encode('cp1251')


@mod.route('/spot/hid/<int:hard_id>', methods=['GET'])
@mod.route('/spot/ean/<barcode>', methods=['GET'])
@xml_headers
@api_admin_access
def api_admin_get_info(hard_id=False, barcode=False):
    """Возвращает информацию о споте по его HID или EAN"""

    if not hard_id and not barcode:
        abort(400)

    if hard_id:
        wallet = PaymentWallet.query.filter_by(
            hard_id=hard_id).first()
        if not wallet:
            abort(404)

        spot = Spot.query.filter_by(
            discodes_id=wallet.discodes_id).first()

    if barcode:
        spot = Spot.query.filter_by(
            barcode=barcode).first()
        if not spot:
            abort(404)

        wallet = PaymentWallet.query.filter_by(
            discodes_id=spot.discodes_id).first()

    return render_template(
        'api/admin/spot_info.xml',
        spot=spot,
        wallet=wallet,
    ).encode('cp1251')


@mod.route('/spot/free', methods=['GET'])
@xml_headers
@api_admin_access
def api_admin_get_free():
    """Возвращает информацию неактивированых спотах"""

    spot = Spot.query.filter_by(
        status=Spot.STATUS_GENERATED).all()
    if not spot:
        abort(404)

    return render_template(
        'api/admin/spot_free.xml',
        spot=spot,
    ).encode('cp1251')


@mod.route('/spot/delete', methods=['POST'])
@xml_headers
@api_admin_access
def api_admin_spot_delete():
    """Удаление спотов"""

    hid = request.form['hid']
    if not hid:
        abort(400)

    wallet = PaymentWallet.query.filter_by(
        hard_id=hid).first()
    if not wallet:
        abort(404)

    history = PaymentHistory.query.filter_by(wallet_id=wallet.id).first()
    if history:
        abort(400)

    spot = Spot.query.filter_by(
        discodes_id=wallet.discodes_id).first()
    if not spot:
        abort(404)

    spot.status = Spot.STATUS_GENERATED
    if not spot.save():
        abort(500)

    wallet.delete()

    return set_message('success', 'Success', 201)
