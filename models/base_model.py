# -*- coding: utf-8 -*-
"""
    Базовая модель

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import logging
import json
from web import db


class BaseModel(object):
    log = logging.getLogger('model')

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()

    def update(self):
        db.session.commit()

    def is_json(self, data_json):
        try:
            json.loads(data_json)
        except:
            return False
        return True

    def encode_field(self, data):
        if not data:
            return None

        if not isinstance(data, (str, unicode)):
            data = str(json.dumps(data))
        return data

    def decode_field(self, data):
        if not data:
            return None

        if not self.is_json(data):
            return data

        if isinstance(data, (str, unicode)):
            data = json.loads(data)
        return data

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.log.error(e)
            return False
        else:
            return True
