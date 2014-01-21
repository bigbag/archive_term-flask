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
    try:
        time.strptime(field.data, '%H:%M')
        return True
    except ValueError:
        raise ValidationError('Bad time format')


class Unique(object):

    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = u'Already exists'
        self.message = message

    def __call__(self, form, field):
        result = self.model.query.filter_by(hard_id=field.data).first()
        if result and result.id != form.data['id']:
            if self.message is None:
                self.message = field.gettext('Already exists.')
            raise ValidationError(self.message)


class TokenSecureForm(Form):

    def generate_csrf_token(self, csrf_context):
        return hash_helper.get_user_token(request)

    def validate_csrf_token(self, field):
        if field.data != hash_helper.get_user_token(request):
            raise ValueError('Invalid CSRF1')
