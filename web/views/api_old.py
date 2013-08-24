# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи для терминального проекта

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

from models.term import Term
from models.term_event import TermEvent
from models.event import Event
from models.person_event import PersonEvent
from models.card_stack import CardStack
from models.payment_wallet import PaymentWallet
from models.payment_lost import PaymentLost
from web.configs.term import TermOldConfig


api_old = Blueprint('api_old', __name__)


@api_old.route('/configs/config_<int:term_id>.xml', methods=['GET'])
@cache.cached(timeout=120)
@xml_headers
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
        'api_old/config.xml',
        term=term,
        config=TermOldConfig,
        term_events=term_events,
        person_events=person_events).encode('cp1251')
    response = make_response(config_xml)

    return response
