# -*- coding: utf-8 -*-
"""
    Базовый класс для форм

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import request

from flask_wtf import Form

from helpers import hash_helper, date_helper


def time_check(form, field):
    try:
        time.strptime(field.data, '%H:%M')
        return True
    except ValueError:
        raise ValidationError('Bad time format')


class TokenSecureForm(Form):

    def generate_csrf_token(self, csrf_context):
        return hash_helper.get_user_token(request)

    def validate_csrf_token(self, field):
        if field.data != hash_helper.get_user_token(request):
            raise ValueError('Invalid CSRF1')
