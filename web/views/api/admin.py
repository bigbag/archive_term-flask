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


@mod.route('/spot/generate', methods=['POST'])
@xml_headers
def api_admin_spot_generate():
    """Генерация спотов"""

    api_admin_access(request)
    count = 10
    if 'count' in request.form:
        try:
            count = int(request.form['count'])
        except Exception as e:
            abort(405)

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

        result[spot.code] = spot.code128

    spot_list = render_template(
        'api/admin/spot_list.xml',
        result=result,
        count=len(result)
    ).encode('cp1251')
    response = make_response(spot_list)

    return spot_list


@mod.route('/spot/linking', methods=['POST'])
@xml_headers
def api_admin_linking_spot():
    """Добавляем спот и связанный с ним кошелёк"""

    api_admin_access(request)
    add_success = 0

    hid = request.form['hid']
    pids = request.form['pids']
    ean = request.form['ean']

    status = 1
    if 'status' in request.form:
        status = request.form['status']

    if not hid or not ean or not pids:
        abort(400)

    if not len(str(ean)) == 13:
        abort(400)

    try:
        hid = int(hid)
        pids = int(pids)
    except Exception as e:
        abort(405)

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

        if status == 0:
            wallet.type = PaymentWallet.TYPE_DEMO
            spot.spot_type_id = Spot.TYPE_DEMO

        if wallet.save():
            spot.status = Spot.STATUS_ACTIVATED
            if not spot.save():
                abort(400)

    if wallet.discodes_id != spot.discodes_id:
        abort(400)

    add_xml = render_template(
        'api/admin/add_info.xml',
        spot=spot,
        wallet=wallet,
        add_success=add_success,
    ).encode('cp1251')

    response = make_response(add_xml)
    return response


@mod.route('/spot/hid/<int:hid>', methods=['GET'])
@mod.route('/spot/ean/<ean>', methods=['GET'])
@mod.route('/spot/code128/<code128>', methods=['GET'])
@xml_headers
def api_admin_get_info(hid=False, ean=False, code128=False):
    """Возвращает информацию о споте по его HID или EAN"""

    api_admin_access(request)
    if not hid and not ean and not code128:
        abort(400)

    try:
        hid = int(hid)
    except Exception as e:
        abort(405)

    if hid:
        wallet = PaymentWallet.query.filter_by(
            hard_id=hid).first()
        if not wallet:
            abort(404)

        spot = Spot.query.filter_by(
            discodes_id=wallet.discodes_id).first()

    if ean or code128:
        if ean and not len(str(ean)) == 13:
            abort(400)

        if ean:
            spot = Spot.query.filter_by(
                barcode=ean).first()
        elif code128:
            spot = Spot.query.filter_by(
                code128=code128).first()
        if not spot:
            abort(404)

        wallet = PaymentWallet.query.filter_by(
            discodes_id=spot.discodes_id).first()

    info_xml = render_template(
        'api/admin/spot_info.xml',
        spot=spot,
        wallet=wallet,
    ).encode('cp1251')
    response = make_response(info_xml)

    return response


@mod.route('/spot/free', methods=['GET'])
@xml_headers
def api_admin_get_free():
    """Возвращает информацию неактивированых спотах"""

    api_admin_access(request)
    spot = Spot.query.filter_by(
        status=Spot.STATUS_GENERATED).all()
    if not spot:
        abort(404)

    info_xml = render_template(
        'api/admin/spot_free.xml',
        spot=spot,
    ).encode('cp1251')
    response = make_response(info_xml)

    return response


@mod.route('/spot/delete', methods=['POST'])
@xml_headers
def api_admin_spot_delete():
    """Удаление спотов"""

    api_admin_access(request)
    hid = request.form['hid']
    if not hid:
        abort(400)

    wallet = PaymentWallet.query.filter_by(
        hard_id=hid, user_id=0).first()
    if not wallet:
        abort(404)

    spot = Spot.query.filter_by(
        discodes_id=wallet.discodes_id).first()
    if not spot:
        abort(404)

    spot.status = Spot.STATUS_GENERATED
    if not spot.save():
        abort(500)

    if wallet:
        wallet.delete()

    return set_message('success', 'Success', 201)
