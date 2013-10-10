# -*- coding: utf-8 -*-
"""
    Базовый класс для форм

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from flask_wtf import Form
from flask import session


class TokenSecureForm(Form):

    def generate_csrf_token(self, csrf_context=1):
        return session.sid

    def validate_csrf_token(self, field):
        if field.data != session.sid:
            raise ValueError('Invalid CSRF1')
