# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи по взаимодействию с соцсетями

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
import os
from flask import Blueprint, abort, request, make_response, render_template
from werkzeug.utils import secure_filename

from web import app

from decorators.header import *
from helpers.error_xml_helper import *

from models.payment_loyalty import PaymentLoyalty
from models.payment_wallet import PaymentWallet
from models.wallet_loyalty import WalletLoyalty
from models.soc_token import SocToken
from models.spot import Spot
from web.views.api import base
from libs.socnet.socnets_api import SocnetsApi

mod = Blueprint('api_social', __name__)


@mod.route('/loyalty', methods=['GET'])
@xml_headers
def api_social_get_loyalties():
    """Возвращает список акций"""

    base._api_access(request)

    count = base._get_request_count(request, PaymentLoyalty.DEFAULT_COUNT)
    offset = base._get_request_offset(request)

    query = PaymentLoyalty.query.order_by(PaymentLoyalty.id)
    loyalties = query.limit(count).offset(offset).all()

    info_xml = render_template(
        'api/social/loyalties_list.xml',
        loyalties=loyalties,
        count=count,
        offset=offset
    ).encode('utf8')

    return make_response(info_xml)


@mod.route('/loyalty/<int:loyalty_id>', methods=['GET'])
@xml_headers
def api_social_get_loyalty(loyalty_id):
    """Возвращает детализацию по акции"""

    base._api_access(request)

    loyalty = PaymentLoyalty.query.get(loyalty_id)
    if not loyalty:
        abort(404)

    wallet_list = []
    wallet_loyalty = WalletLoyalty.query.filter_by(loyalty_id=loyalty.id).all()

    for part in wallet_loyalty:
        if part.wallet_id in wallet_list:
            continue
        wallet_list.append(part.wallet_id)

    spot_ist = []
    part_wallets = PaymentWallet.query.filter(
        PaymentWallet.id.in_(wallet_list)).all()

    for part_wallet in part_wallets:
        if part_wallet.discodes_id in spot_ist:
            continue
        spot_ist.append(part_wallet.discodes_id)

    spots = Spot.query.filter(Spot.discodes_id.in_(spot_ist)).all()

    spot_wallets = []
    for spot in spots:
        for part_wallet in part_wallets:
            if part_wallet.discodes_id != spot.discodes_id:
                continue
            spot_wallets.append(dict(
                discodes_id=spot.discodes_id,
                barcode=spot.barcode,
                hard_id=part_wallet.hard_id
            ))

    info_xml = render_template(
        'api/social/loyalty_info.xml',
        loyalty=loyalty,
        spots=spot_wallets
    ).encode('utf8')

    return make_response(info_xml)


@mod.route('/loyalty/ean/<ean>', methods=['GET'])
@xml_headers
def api_social_spot_loyalty(ean):
    """Возвращает акции, в которых участвует спот по EAN"""

    base._api_access(request)

    ean = str(ean)
    if not len(ean) == 13 or not ean.isdigit():
        abort(400)

    spot = Spot.query.filter_by(barcode=ean).first()
    if not spot:
        abort(404)

    wallet = PaymentWallet.query.filter_by(
        discodes_id=spot.discodes_id).first()
    if not wallet:
        abort(404)

    count = base._get_request_count(request, PaymentLoyalty.DEFAULT_COUNT)
    offset = base._get_request_offset(request)

    if 'id' in request.args:
        # данные только по требуемой акции
        try:
            loyalty_id = int(request.args['id'])
        except:
            abort(405)

        loyalty = PaymentLoyalty.query.get(loyalty_id)
        if not loyalty:
            abort(404)

        wallet_loyalty = WalletLoyalty.query.filter_by(
            loyalty_id=loyalty.id, wallet_id=wallet.id).all()
        if not wallet_loyalty:
            abort(404)

        if not wallet_loyalty[0].checked:
            abort(404)

        loyalties = [loyalty]

    else:
        # по всем акциям спота
        wallet_loyalty = WalletLoyalty.query.filter_by(
            wallet_id=wallet.id).filter_by(checked=1).all()
        if not wallet_loyalty:
            abort(404)

        loyaltyList = []
        for part in wallet_loyalty:
            if part.loyalty_id in loyaltyList:
                continue
            loyaltyList.append(part.loyalty_id)

        query = PaymentLoyalty.query.filter(PaymentLoyalty.id.in_(loyaltyList))
        loyalties = query.limit(count).offset(offset).all()

    info_xml = render_template(
        'api/social/spot_loyalty.xml',
        spot=spot,
        loyalties=loyalties,
        count=count,
        offset=offset
    ).encode('utf8')

    return make_response(info_xml)


@mod.route('/socnet/<ean>', methods=['GET'])
@xml_headers
def api_socnet_list(ean):
    """Список соцсетей, подключенных к споту с правами записи"""
    base._api_access(request)

    ean = str(ean)
    if not len(ean) == 13 or not ean.isdigit():
        abort(400)

    spot = Spot.query.filter_by(barcode=ean).first()
    if not spot:
        abort(404)

    list = spot.getBindedNets()

    info_xml = render_template(
        'api/social/socnet_list.xml',
        spot=spot,
        list=list,
        count=len(list)
    ).encode('utf8')

    return make_response(info_xml)


@mod.route('/socnet/<ean>/<soc_id>', methods=['POST'])
@xml_headers
def api_social_post(ean, soc_id):
    """Публикует пост с картинкой в заданной в soc_id соцсети"""

    base._api_access(request)

    success = 0

    ean = str(ean)
    if not len(ean) == 13:
        abort(400)

    if not 'img' in request.files:
        abort(400)

    file = request.files['img']

    spot = Spot.query.filter_by(barcode=ean).first()
    if not spot:
        abort(404)

    message = ''
    if 'text' in request.form:
        message = request.form['text']

    filesize = 0
    if file:
        file.seek(0, os.SEEK_END)
        filesize = file.tell()
        file.seek(0, os.SEEK_SET)

    filepath = False
    token = False
    error = 'Unknown error'
    img = ''
    if not file or '.' not in file.filename:
        error = 'Incorrect file'
    elif file.filename.rsplit('.', 1)[1] not in app.config['IMG_EXTENSIONS']:
        error = 'usupported file extension'
    elif filesize > app.config['MAX_IMG_LENGTH']:
        error = 'img too large'
    else:
        base_name = secure_filename(file.filename)
        img_name = base_name

        filepath = "%s/%s/%s" % (os.getcwd(), app.config['IMG_FOLDER'],
                                 img_name)

        i = 0
        while (os.path.exists(filepath)):
            i += 1
            img_name = "%s_%s" % (str(i), base_name)
            filepath = "%s/%s/%s" % (os.getcwd(), app.config['IMG_FOLDER'],
                                     img_name)

        file.save(filepath)

        img = "http://%s/%s/%s" % (
            request.host, 'upload/img', img_name)
        img = img.replace('/././', '/')

        error = 'no write rights fo this social account'
        token = SocToken.query.filter_by(
            user_id=spot.user_id, type=soc_id, write_access=1).first()

    if token and img and filepath:
        if SocnetsApi.post_photo(token, token.id, filepath, message):
            success = 1
            error = ''
        else:
            error = 'filed when uploading img to socnet'

    info_xml = render_template(
        'api/social/spot_post.xml',
        spot=spot,
        error=error,
        img=img,
        success=success
    ).encode('utf8')

    return make_response(info_xml)
