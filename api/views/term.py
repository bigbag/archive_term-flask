# -*- coding: utf-8 -*-
"""
Контролер для апи терминального проекта

"""
import json
from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
from api.decorators.header import *
from api import auth, cache
from api.models.term import Term
from api.models.term_event import TermEvent
from api.models.event import Event
from api.models.person_event import PersonEvent
from api.models.wallet import Wallet
from api.configs.general import TermConfig


term = Blueprint('term', __name__)


@term.route('/configs/config_<int:id>.xml', methods=['GET'])
#@cache.memoize(timeout=60)
# @auth.login_required
@xml_headers
@add_md5
def get_config(id):
    """Возвращает конфигурационный файл для терминала"""
    term = Term(id).get_term()

    if not term:
        abort(400)

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
#@cache.memoize(timeout=60)
@xml_headers
@add_md5
def blacklist():
    """Возвращает черный список карт"""
    wallets = Wallet.query.filter(
        (Wallet.balance == 0) | (Wallet.status == -1)).all()

    config_xml = render_template(
        'term/blacklist.xml',
        wallets=wallets).encode('cp1251')

    response = make_response(config_xml)

    return response
