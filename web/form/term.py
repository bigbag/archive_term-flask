# -*- coding: utf-8 -*-
"""
    Формы для терминалов

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


class TermAddForm(TokenSecureForm):

    id = IntegerField(validators=[InputRequired()])
    name = TextField(validators=[InputRequired()])
    type = DecimalField(places=1, validators=[InputRequired()])
    upload_start = TextField(validators=[Optional(), base.time_check])
    upload_period = IntegerField(default=5)
    download_start = TextField(validators=[Optional(), base.time_check])
    download_period = IntegerField(default=5)
