# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи администрирования

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import Blueprint, abort, request, make_response, render_template

from decorators.header import *
from helpers.error_xml_helper import *

from models.spot import Spot
from models.spot_color import SpotColor
from models.spot_pattern import SpotPattern
from models.spot_hard import SpotHard
from models.spot_hard_type import SpotHardType
from models.spot_dis import SpotDis
from models.payment_wallet import PaymentWallet
from models.spot_troika import SpotTroika

from external_services import troika as troika_api

from web.views.api import base


mod = Blueprint('api_admin', __name__)


@mod.route('/spot/generate', methods=['POST'])
@xml_headers
def api_admin_spot_generate():
    """Генерация спотов"""

    base._api_access(request)

    count = 10
    if 'count' in request.form:
        try:
            count = int(request.form['count'])
        except:
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

    return spot_list


@mod.route('/spot/linking', methods=['POST'])
@xml_headers
def api_admin_linking_spot():
    """Добавляем спот и связанный с ним кошелёк"""

    base._api_access(request)
    add_success = 0

    hid = request.form['hid']
    pids = request.form['pids']
    ean = request.form['ean']

    hard_type = Spot.DEFAULT_HARD_TYPE
    if 'hard_type' in request.form:
        hard_type = int(request.form['hard_type'])
        if not SpotHardType.query.get(hard_type):
            abort(400)

    status = 1
    if 'status' in request.form:
        status = int(request.form['status'])

    if not hid or not ean or not pids:
        abort(400)

    if not len(str(ean)) == 13:
        abort(400)

    try:
        hid = int(hid)
        pids = int(pids)
    except Exception:
        abort(405)

    spot = Spot.query.filter_by(
        barcode=ean).first()
    if not spot:
        abort(404)

    spot.hard_type = hard_type

    troika_info = troika_api.release_card(hid)
    if troika_info:
        spot.user_id = troika_info['user_id']

        spot_troika = SpotTroika()
        spot_troika.discodes_id = spot.discodes_id
        spot_troika.save()

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

        if troika_info:
            wallet.user_id = troika_info['user_id']
            wallet.status = PaymentWallet.STATUS_ACTIVE

        if wallet.save():
            spot.status = Spot.STATUS_ACTIVATED

            if troika_info:
                spot.status = Spot.STATUS_REGISTERED

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


@mod.route('/spot/hid/<int:hid>', methods=['GET'])
@mod.route('/spot/ean/<ean>', methods=['GET'])
@mod.route('/spot/code128/<code128>', methods=['GET'])
@xml_headers
def api_admin_get_info(hid=False, ean=False, code128=False):
    """Возвращает информацию о споте по его HID или EAN"""

    base._api_access(request)
    if not hid and not ean and not code128:
        abort(400)

    try:
        hid = int(hid)
    except:
        abort(405)

    wallet = None
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

    troika_info = None
    if wallet:
        troika_info = troika_api.get_card_by_hard_id(wallet.hard_id)

    info_xml = render_template(
        'api/admin/spot_info.xml',
        spot=spot,
        wallet=wallet,
        troika=troika_info,
    ).encode('cp1251')
    response = make_response(info_xml)

    return response


@mod.route('/spot/free', methods=['GET'])
@xml_headers
def api_admin_get_free():
    """Возвращает информацию неактивированых спотах"""

    base._api_access(request)
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


@mod.route('/spot/unlink', methods=['POST'])
@xml_headers
def api_admin_spot_unlink():
    """Удаление кошелька, очистка спота"""

    base._api_access(request)
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

    if not spot.clear():
        abort(500)

    wallet.delete()

    return set_message('success', 'Success', 201)


@mod.route('/spot/delete', methods=['POST'])
@xml_headers
def api_admin_spot_delete():
    """Удаление спотов"""
    base._api_access(request)
    code128 = request.form['code128']
    if not code128:
        abort(400)

    spot = Spot.query.filter_by(
        code128=code128).first()
    if not spot or spot.user_id:
        abort(404)

    wallet = PaymentWallet.query.filter_by(
        discodes_id=spot.discodes_id).first()
    if wallet:
        abort(400)

    if not spot.clear():
        abort(500)

    spot.delete()

    return set_message('success', 'Success', 201)


@mod.route('/spot/hard/color', methods=['GET'])
@xml_headers
def api_admin_spot_color():
    """Возвращает информацию о доступных для спота цветах"""

    base._api_access(request)
    return api_admin_hard_list(SpotColor, request)


@mod.route('/spot/hard/pattern', methods=['GET'])
@xml_headers
def api_admin_spot_pattern():
    """Возвращает информацию о доступных для спота шаблонах"""

    base._api_access(request)
    return api_admin_hard_list(SpotPattern, request)


@mod.route('/spot/hard/model', methods=['GET'])
@xml_headers
def api_admin_spot_model():
    """Возвращает информацию о доступных для спота корпусах"""

    base._api_access(request)
    return api_admin_hard_list(SpotHard, request)


def api_admin_hard_list(model, request):

    query = model.query

    args = request.args
    if 'show' in args:
        query = query.filter_by(show=request.args.get('show'))

    data = query.all()
    if not data:
        abort(404)

    info_xml = render_template(
        'api/admin/hard_list.xml',
        data=data,
        count=len(data)
    ).encode('utf8')
    return make_response(info_xml)


@mod.route('/spot/hard/type', methods=['GET'])
@xml_headers
def api_admin_spot_hard_type():
    """Возвращает информацию о типах спотов"""

    base._api_access(request)
    query = SpotHardType.query

    args = request.args
    if 'show' in args:
        query = query.filter_by(show=request.args.get('show'))
    if 'color_id' in args:
        query = query.filter_by(color_id=request.args.get('color_id'))
    if 'pattern_id' in args:
        query = query.filter_by(pattern_id=request.args.get('pattern_id'))
    if 'hard_id' in args:
        query = query.filter_by(hard_id=request.args.get('hard_id'))

    data = query.all()
    if not data:
        abort(404)

    info_xml = render_template(
        'api/admin/hard_type_list.xml',
        data=data,
        count=len(data)
    ).encode('utf8')
    return make_response(info_xml)
