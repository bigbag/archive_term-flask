# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи для терминального проекта

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os
import json
from web import app
from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
from web.decorators.header import *
from web.helpers.date_helper import *
from web.helpers.hash_helper import *
from web import auth, cache
from web.models.term import Term
from web.models.term_event import TermEvent
from web.models.event import Event
from web.models.person_event import PersonEvent
from web.models.card_stack import CardStack
from web.models.payment_wallet import PaymentWallet
from web.models.payment_lost import PaymentLost
from web.configs.term import TermConfig


api = Blueprint('api', __name__)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Fail'}), 500)


@api.route('/configs/config_<int:term_id>.xml', methods=['GET'])
@cache.cached(timeout=60)
# @auth.login_required
@xml_headers
@md5_content_headers
def get_config(term_id):
    """Возвращает конфигурационный файл для терминала"""
    term_db = Term(term_id).get_term()

    if term_db is None:
        abort(400)

    term = term_db.get_xml_view()

    term_events = TermEvent.query.filter_by(
        term_id=term.id).all()

    if term_events is None:
        abort(400)

    person_events = PersonEvent.query.filter_by(
        term_id=term.id).all()

    config_xml = render_template(
        'term/config.xml',
        term=term,
        config=TermConfig,
        term_events=term_events,
        person_events=person_events).encode('cp1251')
    response = make_response(config_xml)

    return response


@api.route('/configs/blacklist.xml', methods=['GET'])
@cache.cached(timeout=60)
@xml_headers
@md5_content_headers
def get_blacklist():
    """Возвращает черный список карт"""
    wallets = PaymentWallet.query.filter(
        (PaymentWallet.balance == 0) | (PaymentWallet.status == -1)).all()

    lost_cards = PaymentLost.query.all()

    config_xml = render_template(
        'term/blacklist.xml',
        wallets=wallets,
        lost_cards=lost_cards,
    ).encode('cp1251')

    response = make_response(config_xml)

    return response


@api.route('/reports/report_<int:term_id>_<report_datetime>.xml', methods=['PUT'])
def upload_report(term_id, report_datetime):
    """Прием и сохранение отчета"""

    if not len(report_datetime) == 13:
        abort(400)

    m = re.search('\d{6}_\d{6}', str(report_datetime))

    if not m:
        abort(400)

    term = Term(term_id).get_term()

    if term is None:
        abort(400)

    term.report_date = get_curent_date()
    term.update()

    file = request.stream.read()
    filename = "%s/%s_%s" % (
        app.config['UPLOAD_TMP'],
        str(term_id),
        str(report_datetime))

    if not request.headers.get('Content-MD5'):
        abort(400)

    if request.headers.get('Content-MD5') != get_content_md5(file):
        abort(400)

    if file:
        with open(filename, 'w') as f:
            f.write(file)
    else:
        abort(400)

    return make_response(jsonify({'success': 'Report uploaded successfully'}), 201)


@api.route('/uids/<int:term_id>_<payment_id>.uid', methods=['PUT'])
def add_card(term_id, payment_id):
    """Добавляем в базу карту для привязки"""

    term = Term(term_id).get_term()

    if not term:
        abort(400)

    if CardStack.query.filter_by(payment_id=payment_id).first():
        abort(400)

    card = CardStack()
    card.term_id = term_id
    card.payment_id = payment_id
    card.save()

    return make_response(jsonify({'success': 'Card added'}), 201)
