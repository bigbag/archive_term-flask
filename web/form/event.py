# -*- coding: utf-8 -*-
"""
    Формы для событий

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
import wtforms_json

from flask_wtf import Form
from wtforms import TextField, DecimalField, IntegerField, ValidationError
from wtforms.validators import *

from web.form.base import TokenSecureForm
from webform import base


class TermEventAddForm(TokenSecureForm):

    id = IntegerField(validators=[InputRequired()])
    term_id = IntegerField(InputRequired())
    event_id = IntegerField(InputRequired())
    start = TextField(validators=[Optional(), base.time_check])
    stop = TextField(validators=[Optional(), base.time_check])
