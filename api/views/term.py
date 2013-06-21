# -*- coding: utf-8 -*-
from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
import json
from api.decorators.header import *
from api.helpers.date_helper import *
from api import auth, cache
from api.models.term import Term


term = Blueprint('term', __name__)


@term.route('/configs/config_<int:id>.xml', methods=['GET'])
@xml_headers
@cache.memoize(timeout=0)
#@auth.login_required
def get_config(id):
    """Возвращает конфигурационный файл для терминала"""
    term = Term.query.filter_by(id=id, status=Term.STATUS_VALID).first()

    if not term:
        abort(400)

    term.download = json.loads(term.download)
    term.upload = json.loads(term.upload)
    config_xml = render_template('term/config.xml', term=term)
    response = make_response(config_xml)

    return response
