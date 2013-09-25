# -*- coding: utf-8 -*-
"""
    Хелпер заменяющий стандартные сообщения об ощибках, формат html

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask, render_template, current_app
from decorators.header import *


def get_error(message, code):
    firm_info = get_firm_name(request)
    return render_template(
        'term/error.html',
        message=message,
        code=code,
        firm_name=firm_info['name']), code


@current_app.errorhandler(400)
def bag_request(error):
return get_error('Bad request', 400)


@current_app.errorhandler(404)
def not_found(error):
return get_error('Not found', 404)


@current_app.errorhandler(405)
def method_not_allowed(error):
return get_error('Method Not Allowed', 405)
