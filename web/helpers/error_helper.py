# -*- coding: utf-8 -*-
"""
    Хелпер заменяющий стандартные сообщения об ощибках

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from flask import Flask, jsonify, make_response


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Fail'}), 500)
