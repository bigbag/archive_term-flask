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
from helpers.error_xml_helper import *

from helpers import hash_helper

from models.spot import Spot
from models.spot_dis import SpotDis
from models.payment_wallet import PaymentWallet
from models.term_user import TermUser


api_admin = Blueprint('api_admin', __name__)


def api_admin_access(request):
    headers = request.headers
    if not 'Key' in headers or 'Sign' not in headers:
        abort(400)

    term_user = TermUser().get_by_api_key(headers['Key']);

    if not term_user:
        abort(403)
    true_sign = hash_helper.get_api_sign(
        str(term_user.api_secret),
        request.form)

    if not true_sign == headers['Sign']:
        abort(403)


@api_admin.route('/spot/generate', methods=['POST'])
@xml_headers
def spot_generate():
    """Генерация спотов"""
    api_admin_access(request)

    count = 10
    if 'count' in request.form:
        count = int(request.form['count'])
        count = 1 if count > 100 else count

    dis = SpotDis().get_new_list(count)

    result = {}
    for row in dis:
        row.status = SpotDis.STATUS_GENERATED
        if not row.save():
            continue

        spot = Spot()
        spot.discodes_id = row.id

        if not spot.save():
            row.status = SpotDis.STATUS_INIT
            row.save()
            continue

        result[spot.code] = spot.barcode

    spot_list = render_template(
        'api/admin/spot_list.xml',
        result=result,
    ).encode('cp1251')
    response = make_response(spot_list)

    return spot_list


@api_admin.route('/spot/linking', methods=['POST'])
@xml_headers
def linking_spot():
    """Добавляем спот и связанный с ним кошелёк"""
    api_admin_access(request)
    add_success = 0

    hid = request.form['hid']
    pids = request.form['pids']
    ean = request.form['ean']

    if not hid or not ean or not pids:
        abort(400)

    if not len(str(pids)) == 10 or not len(str(ean)) == 13:
        abort(400)

    hid = int(hid)
    pids = int(pids)

    spot = Spot.query.filter_by(
        barcode=ean).first()

    if not spot:
        abort(400)

    wallet = PaymentWallet.query.filter_by(
        hard_id=hid).first()

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

    add_xml = render_template(
        'api/admin/add_info.xml',
        spot=spot,
        wallet=wallet,
        add_success=add_success,
    ).encode('cp1251')

    response = make_response(add_xml)

    return response


@api_admin.route('/spot/<int:hard_id>', methods=['GET'])
@xml_headers
def get_info(hard_id):
    """Возвращает информацию о споте по его HID"""
    api_admin_access(request)

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
        'api/admin/spot_info.xml',
        spot=spot,
        wallet=wallet,
    ).encode('cp1251')

    response = make_response(info_xml)

    return response


@api_admin.route('/spot/free', methods=['GET'])
@xml_headers
def get_free():
    """Возвращает информацию неактивированых спотах"""

    spot = Spot.query.filter_by(
        status=Spot.STATUS_GENERATED).all()

    info_xml = render_template(
        'api/admin/spot_free.xml',
        spot=spot,
    ).encode('cp1251')

    response = make_response(info_xml)

    return response


@api_admin.route('/spot/delete', methods=['POST'])
@xml_headers
def spot_delete():
    """Удаление спотов"""
    api_admin_access(request)

    ean = request.form['ean']
    if not ean:
        abort(400)

    if not len(str(ean)) == 13:
        abort(400)

    spot = Spot.query.filter(((Spot.status == Spot.STATUS_GENERATED) |
                            (Spot.status == Spot.STATUS_ACTIVATED)) &
        (Spot.barcode == ean)).first()

    if not spot:
        abort(404)

    if spot.delete():
        wallet = PaymentWallet.query.filter_by(
            discodes_id=spot.discodes_id).first()

        if wallet:
            wallet.delete()

    return set_message('success', 'Success', 201)
