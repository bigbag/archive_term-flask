# -*- coding: utf-8 -*-
"""
    Набор базовых функций для api

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import abort
from models.term_user import TermUser

from helpers import hash_helper


def _api_access(request):
    """Проверка прав на доступ к апи"""

    headers = request.headers
    if 'Key' not in headers or 'Sign' not in headers:
        abort(400)

    term_user = TermUser().get_by_api_key(headers['Key'])
    if not term_user:
        abort(403)

    true_sign = hash_helper.get_api_sign(
        str(term_user.api_secret),
        request.form)
    if not true_sign == headers['Sign']:
        abort(403)


def _get_request_count(request, max):
    limit = request.args.get('count', max)
    try:
        limit = int(limit)
    except Exception as e:
        abort(405)
    if limit > max:
        limit = max

    return limit


def _get_request_offset(request):
    offset = request.args.get('offset', 0)
    try:
        offset = int(offset)
    except Exception as e:
        abort(405)

    return offset
