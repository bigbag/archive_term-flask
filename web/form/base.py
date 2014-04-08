# -*- coding: utf-8 -*-
"""
    Базовый класс для форм

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time

from flask import request
from wtforms import ValidationError

from flask_wtf import Form

from helpers import hash_helper, date_helper


def time_check(form, field):
    result = date_helper.validate_date(field.data, '%H:%M')
    if not result:
        raise ValidationError('Bad time format')
    else:
        return True


class TokenSecureForm(Form):

    def generate_csrf_token(self, csrf_context):
        return hash_helper.get_user_token(request)

    def validate_csrf_token(self, field):
        if field.data != hash_helper.get_user_token(request):
            raise ValueError('Invalid CSRF')
