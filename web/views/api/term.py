# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи для терминального проекта

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os

from flask import Blueprint, abort, request, make_response, url_for, render_template

from web import app, cache

from decorators.header import *
from helpers.error_xml_helper import *
from helpers import date_helper, hash_helper

from models.term import Term
from models.term_event import TermEvent
from models.event import Event
from models.person_event import PersonEvent
from models.card_stack import CardStack
from models.payment_wallet import PaymentWallet
from models.term_settings import TermSettings
from models.alarm_stack import AlarmStack
from models.term_blacklist import TermBlacklist


from web.tasks.report_parser import ReportParserTask

mod = Blueprint('api_term', __name__)


@mod.route('/configs/config_<int:term_id>.xml', methods=['GET'])
@cache.cached(timeout=30, key_prefix='term_xml_config')
@md5_content_headers
@xml_headers
def api_get_xml_config(term_id):
    return api_get_config(term_id)


@mod.route('/configs/config_<int:term_id>.xml.gz', methods=['GET'])
@cache.cached(timeout=30, key_prefix='term_gzip_config')
@md5_content_headers
@gzip_content
def api_get_gzip_config(term_id):
    return api_get_config(term_id)


def api_get_config(term_id):
    """Возвращает конфигурационный файл для терминала"""
    term = Term.get_valid_term(int(term_id))

    if term is None:
        abort(400)

    term = term.get_xml_view()
    term_settings = TermSettings.query.get(term.settings_id)

    if term.status == Term.STATUS_BANNED:
        config_xml = render_template(
            'api/term/config_empty.xml',
            term=term,
            config=term_settings).encode('cp1251')
        response = make_response(config_xml)
    else:
        term_events = TermEvent().get_by_term_id(term.id)
        if term_events is None:
            abort(400)

        person_events = PersonEvent.get_valid_by_term_id(term.id)

        config_xml = render_template(
            'api/term/config.xml',
            term=term,
            config=term_settings,
            term_events=term_events,
            person_events=person_events).encode('cp1251')
        response = make_response(config_xml)

    return response


@mod.route('/configs/blacklist.xml', methods=['GET'])
@mod.route('/configs/blacklist_<int:timestamp>.xml', methods=['GET'])
# @cache.cached(timeout=30, key_prefix='term_xml_blacklist')
@md5_content_headers
@xml_headers
def api_get_xml_blacklist(timestamp=None):
    return api_get_blacklist(timestamp)


@mod.route('/configs/blacklist.xml.gz', methods=['GET'])
@mod.route('/configs/blacklist_<int:timestamp>.xml.gz', methods=['GET'])
# @cache.cached(timeout=30, key_prefix='term_gzip_blacklist')
@md5_content_headers
@gzip_content
def api_get_gzip_blacklist(timestamp=None):
    return api_get_blacklist(timestamp)


def api_get_blacklist(timestamp=None):
    """Возвращает черный список карт"""

    if not timestamp:
        blacklist = TermBlacklist.query.filter(
            TermBlacklist.status == TermBlacklist.STATUS_BLACK).all()
    else:
        blacklist = TermBlacklist.query.filter(
            TermBlacklist.timestamp > timestamp).all()

    config_xml = render_template(
        'api/term/blacklist.xml',
        blacklist=blacklist,
        max_timestamp=TermBlacklist.get_max_timestamp(),
    ).encode('cp1251')

    return make_response(config_xml)


@mod.route('/reports/report_<int:term_id>_<report_datetime>.xml.gz', methods=['PUT'])
@mod.route('/reports/report_<int:term_id>_<report_datetime>.xml', methods=['PUT'])
def api_upload_report(term_id, report_datetime):
    """Прием и сохранение отчета"""

    if not len(report_datetime) == 13:
        abort(400)

    if not re.search('\d{6}_\d{6}', str(report_datetime)):
        abort(400)

    term = Term.get_valid_term(term_id)

    if term is None:
        abort(400)

    file = request.stream.read()
    filename = "%s/%s_%s" % (
        app.config['REPORT_TMP_PACH'],
        str(term_id),
        str(report_datetime))

    if not request.headers.get('Content-MD5'):
        abort(400)

    if request.headers.get('Content-MD5') != hash_helper.get_content_md5(file):
        abort(400)

    if file:
        with open(filename, 'w') as f:
            f.write(file)
    else:
        abort(400)

    term.report_date = date_helper.get_curent_date()
    term.save()

    ReportParserTask.report_manager.delay(filename)

    return set_message('success', hash_helper.get_content_md5(file), 201)


@mod.route('/reports/log_<filename>', methods=['PUT'])
def api_upload_log(filename):
    """Прием и сохранение логов"""

    file = request.stream.read()
    filename = "%s/%s" % (
        app.config['UPLOAD_LOG'], filename)
    if file:
        with open(filename, 'w') as f:
            f.write(file)
    else:
        abort(400)

    return set_message('success', hash_helper.get_content_md5(file), 201)


@mod.route('/configs/callback/<int:term_id>_<action>', methods=['POST'])
@mod.route('/configs/callback/<int:term_id>_<action>_<version>', methods=['POST'])
def api_set_callback(term_id, action, version=None):
    """Сообщение об удачной загрузки настроек или черного списка"""

    VALID_ACTITON = (
        'config',
        'blacklist'
    )
    if not action in VALID_ACTITON:
        abort(405)

    term = Term.get_valid_term(term_id)

    if term is None:
        abort(404)

    if action == 'config':
        term.config_date = date_helper.get_curent_date()
        AlarmStack.reset_count(term.id)
    elif action == 'blacklist':
        term.blacklist_date = date_helper.get_curent_date()

    term.save()

    return set_message('success', 'Success', 201)
