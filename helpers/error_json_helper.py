# -*- coding: utf-8 -*-
"""
    Хелпер заменяющий стандартные сообщения об ощибках, формат json

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from flask import jsonify, make_response
from decorators.header import *


@app.errorhandler(400)
@json_headers
def bag_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
@json_headers
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(405)
@json_headers
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method Not Allowed'}), 405)


@app.errorhandler(500)
@json_headers
def fail(error):
    return make_response(jsonify({'error': 'Fail'}), 500)
