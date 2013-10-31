# -*- coding: utf-8 -*-
"""
    Формы для событий

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import wtforms_json

from flask_wtf import Form
from wtforms import TextField, DecimalField, IntegerField, ValidationError
from wtforms.validators import *

from web.form.base import TokenSecureForm
from web.form import base

wtforms_json.init()


class TermEventAddForm(TokenSecureForm):

    id = IntegerField()
    age = IntegerField(default=0)
    cost = IntegerField(default=0)
    timeout = IntegerField(default=0)
    start = TextField(validators=[Optional(), base.time_check])
    stop = TextField(validators=[Optional(), base.time_check])
    term_id = IntegerField(InputRequired())
    event_id = IntegerField(InputRequired())
