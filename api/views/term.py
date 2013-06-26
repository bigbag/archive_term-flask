# -*- coding: utf-8 -*-
"""
Контролер для апи терминального проекта

"""
import re
import os
import json
from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
from api.decorators.header import *
from api.helpers.date_helper import *
from api.helpers.hash_helper import *
from api import auth, cache
from api.models.term import Term
from api.models.term_event import TermEvent
from api.models.event import Event
from api.models.person_event import PersonEvent
from api.models.card_stack import CardStack
from api.models.wallet import Wallet
from api.configs.general import TermConfig


term = Blueprint('term', __name__)


@term.route('/configs/config_<int:term_id>.xml', methods=['GET'])
@cache.cached(timeout=60)
# @auth.login_required
@xml_headers
@md5_content_headers
def get_config(term_id):
    """Возвращает конфигурационный файл для терминала"""
    term = Term(term_id).get_term()

    if not term:
        abort(400)

    term.download = json.loads(term.download)
    term.upload = json.loads(term.upload)

    if term.type == Term.TYPE_VENDING:
        term.type = 'Vending'
    elif term.type == Term.TYPE_POS:
        term.type = 'Normal'

    term_events = TermEvent.query.filter_by(
        term_id=term.id).all()

    if not term_events:
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


@term.route('/configs/blacklist.xml', methods=['GET'])
@cache.cached(timeout=60)
@xml_headers
@md5_content_headers
def get_blacklist():
    """Возвращает черный список карт"""
    wallets = Wallet.query.filter(
        (Wallet.balance == 0) | (Wallet.status == -1)).all()

    config_xml = render_template(
        'term/blacklist.xml',
        wallets=wallets).encode('cp1251')

    response = make_response(config_xml)

    return response


@term.route('/reports/report_<int:term_id>_<report_datetime>.xml', methods=['PUT'])
def set_report(term_id, report_datetime):
    """Прием и сохранение отчета"""

    if not len(report_datetime) == 13:
        abort(400)

    m = re.search('\d{6}_\d{6}', str(report_datetime))

    if not m:
        abort(400)

    term = Term(term_id).get_term()

    if not term:
        abort(400)

    term.report_date = get_curent_date()
    term.update()

    report_datetime = str(report_datetime).split('_')
    report_date = report_datetime[0]
    report_time = report_datetime[1]

    file = request.stream.read()
    file_patch = app.config['UPLOAD_FOLDER'] + '/' + report_date

    if not request.headers.get('Content-MD5'):
        abort(400)

    if request.headers.get('Content-MD5') != get_content_md5(file):
        abort(400)

    if file:
        if not os.path.exists(file_patch):
            os.makedirs(file_patch)

        filename = os.path.join(
            file_patch, str(term_id) + "_" + report_time)
        with open(filename, 'a') as f:
            f.write(file)
    else:
        abort(400)

    return make_response(jsonify({'success': 'Report uploaded successfully'}), 201)


@term.route('/uids/<int:term_id>_<payment_id>.uid', methods=['PUT'])
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
