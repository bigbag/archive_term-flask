# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи администрирования

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os

from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for, render_template
from web import app
from web import cache

term = Blueprint('term', __name__)


@term.route('/', methods=['GET'])
def spot_generate():
    """Генерация спотов"""

    return '1'
