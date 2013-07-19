# -*- coding: utf-8 -*-
"""
    Модель для спотов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import random
import string
import hashlib

from web import db
from web.helpers.date_helper import *
from web.helpers.hash_helper import *


class Spot(db.Model):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot'

    STATUS_GENERATED = 0
    STATUS_ACTIVATED = 1
    STATUS_REGISTERED = 2
    STATUS_CLONES = 3
    STATUS_REMOVED_USER = 4
    STATUS_REMOVED_SYS = 5
    STATUS_INVISIBLE = 6

    TYPE_PERSONAL = 3
    TYPE_COUPON = 4
    TYPE_CARD = 8
    TYPE_FEEDBACK = 9

    CODE_SIZE = 10

    discodes_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(300))
    url = db.Column(db.String(150), nullable=False)
    barcode = db.Column(db.String(32), nullable=False, unique=True)
    spot_type_id = db.Column(db.Integer)
    lang = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, index=True)
    premium = db.Column(db.Integer, nullable=False)
    generated_date = db.Column(db.DateTime, nullable=False)
    registered_date = db.Column(db.DateTime)
    removed_date = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False, index=True)

    def __init__(self):
        self.lang = 'en'
        self.name = 'No name'
        self.status = self.STATUS_GENERATED
        self.spot_type_id = self.TYPE_PERSONAL

    def __repr__(self):
        return '<discodes_id %r>' % (self.discodes_id)

    def get_random_string(self, char=string.letters, size=CODE_SIZE):
        return ''.join(random.choice(char) for x in range(size))

    def get_code(self):
        id_ = self.discodes_id

        rnd_letters = list(self.get_random_string())
        rnd_order = range(10)
        random.shuffle(rnd_order)
        rnd_order = sorted(rnd_order[:6])

        for x in xrange(0, 6):
            rnd_letters[rnd_order[x]] = id_[x]

        return ''.join(rnd_letters)

    def get_barcode(self):
        rnd = str(random.randint(1000000000, 9999999999))
        ean = "00%s%s" % (rnd, get_ean_checksum(rnd))

        spot = self.query.filter_by(barcode=ean).first()
        if spot:
            self.get_barcode
        else:
            return ean

    def get_url(self):
        if not self.barcode:
            self.barcode = self.get_barcode()

        url = hashlib.sha1(self.barcode).hexdigest()
        url = url[:15]

        spot = self.query.filter_by(url=url).first()
        if spot:
            self.get_url
        else:
            return url

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            if not self.creation_date:
                self.creation_date = get_curent_date()

            if not self.registered_date and self.status == self.STATUS_REGISTERED:
                self.registered_date = get_curent_date()

            if not self.removed_date:
                if self.status == self.STATUS_REMOVED_USER or self.status == self.STATUS_REMOVED_SYS:
                    self.removed_date = get_curent_date()

            if not self.url:
                self.url = self.get_url()

            if not self.code:
                self.code = self.get_code()

            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
            return False
        else:
            return True
