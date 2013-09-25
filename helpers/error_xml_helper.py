# -*- coding: utf-8 -*-
"""
    Хелпер заменяющий стандартные сообщения об ощибках, формат xml

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import app
from flask import Flask, make_response, render_template_string, current_app
from decorators.header import *

message_template = """<?xml version="1.0" encoding="windows-1251"?>
    <message type="{{type}}">{{message}}</message>
    """


def set_message(message_type, message, code):
    message_xml = render_template_string(
        message_template,
        type=message_type,
        message=message).encode('cp1251')

    return make_response(message_xml, code)


@app.errorhandler(400)
@xml_headers
def bag_request(error):
    return set_message('error', 'Bad request', 400)


@app.errorhandler(404)
@xml_headers
def not_found(error):
    return set_message('error', 'Not found', 404)


@app.errorhandler(405)
@xml_headers
def method_not_allowed(error):
    return set_message('error', 'Method Not Allowed', 405)


@app.errorhandler(500)
@xml_headers
def method_not_allowed(error):
    return set_message('error', 'Fail', 500)
