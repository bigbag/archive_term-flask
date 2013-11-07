# -*- coding: utf-8 -*-
"""
    Формы для людей

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import wtforms_json

from flask_wtf import Form
from wtforms import TextField, DecimalField, IntegerField, DateTimeField
from wtforms.validators import *

from web.form.base import TokenSecureForm
from web.form import base

wtforms_json.init()


class PersonAddForm(TokenSecureForm):

    id = IntegerField(validators=[InputRequired()])
    first_name = TextField(validators=[InputRequired()])
    midle_name = TextField()
    last_name = TextField(validators=[InputRequired()])
    tabel_id = IntegerField()
    birthday = DateTimeField()
    firm_id = IntegerField(validators=[InputRequired()])
    card = TextField()
    payment_id = TextField()
    hard_id = TextField()
    status = IntegerField()
