# -*- coding: utf-8 -*-
"""
    Модель для спотов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import random
import string
import hashlib

from flask import g

from web import db
from helpers import date_helper, hash_helper

from models.base_model import BaseModel

from models.user import User
from models.soc_token import SocToken


class Spot(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'spot'

    STATUS_GENERATED = 0
    STATUS_ACTIVATED = 1
    STATUS_REGISTERED = 2
    STATUS_CLONES = 3
    STATUS_REMOVED_USER = 4
    STATUS_REMOVED_SYS = 5
    STATUS_INVISIBLE = 6

    TYPE_DEMO = 0
    TYPE_FULL = 3

    CODE_SIZE = 10
    MAX_GENERATE = 101
    CODE128_LEN = 12
    EAN_LEN = 12

    DEFAULT_HARD_TYPE = 1

    CODE_CHAR = 'abcdefghjkmnopqrstuvwxyzABCDEFGHJKMNOPQRSTUVWXYZ'

    discodes_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(300))
    url = db.Column(db.String(150), nullable=False)
    barcode = db.Column(db.String(32), nullable=False)
    type = db.Column(db.Integer)
    lang = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    premium = db.Column(db.Integer, nullable=False)
    generated_date = db.Column(db.DateTime, nullable=False)
    registered_date = db.Column(db.DateTime)
    removed_date = db.Column(db.DateTime)
    status = db.Column(db.Integer, nullable=False, index=True)
    code128 = db.Column(db.String(128), nullable=False)
    hard_type = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.lang = 'en'
        self.name = 'No name'
        self.premium = 0
        self.status = self.STATUS_GENERATED
        self.type = self.TYPE_FULL
        self.hard_type = self.DEFAULT_HARD_TYPE
        self.generated_date = date_helper.get_current_date()

    def __repr__(self):
        return '<discodes_id %r>' % (self.discodes_id)

    def get_random_string(self, char=string.letters, size=CODE_SIZE):
        return ''.join(random.choice(char) for x in range(size))

    def get_code(self, discodes_id):
        discodes_id = str(discodes_id)
        rnd_letters = list(self.get_random_string(char=self.CODE_CHAR))
        rnd_order = range(10)
        random.shuffle(rnd_order)
        rnd_order = sorted(rnd_order[:6])

        for x in xrange(0, 6):
            rnd_letters[rnd_order[x]] = discodes_id[x]

        return ''.join(rnd_letters)

    def get_barcode(self):
        rnd = str(random.randint(1000000000, 9999999999))
        ean = "00%s%s" % (rnd, hash_helper.get_ean_checksum(rnd))

        spot = Spot.query.filter_by(barcode=ean).first()
        if spot:
            self.get_barcode
        else:
            self.barcode = ean
            return True

    def get_max_code128(self):
        if 'max_code128' not in g:
            spot = Spot.query.order_by('code128 DESC').first()
            if spot:
                return spot.code128
        else:
            return g.max_code128
        return False

    def gen_code128(self):

        max_code = self.get_max_code128()
        self.code128 = 1
        if max_code:
            self.code128 = int(max_code) + 1

        self.code128 = str(self.code128).rjust(self.CODE128_LEN, '0')
        return True

    def get_url(self):
        if not self.barcode:
            self.get_barcode()

        random_part = random.randint(1000000000, 9999999999)
        data = "%s%s" % (str(self.barcode), str(random_part))
        url = hashlib.sha1(data).hexdigest()
        url = url[:15]

        spot = Spot.query.filter_by(url=url).first()
        if spot:
            self.get_url
        else:
            self.url = url
            return True

    def get_valid_by_code(self, code):
        valid_status = [
            self.STATUS_ACTIVATED,
            self.STATUS_REGISTERED,
            self.STATUS_CLONES
        ]
        return Spot.query.filter(
            Spot.code == code).filter(
                Spot.status.in_(valid_status)).first()

    def save(self):
        if not self.registered_date and self.status == self.STATUS_REGISTERED:
            self.registered_date = date_helper.get_current_date()

        if not self.removed_date:
            if self.status == self.STATUS_REMOVED_USER or self.status == self.STATUS_REMOVED_SYS:
                self.removed_date = date_helper.get_current_date()

        if not self.url:
            self.get_url()

        if not self.code128:
            self.gen_code128()
            g.max_code128 = self.code128

        if not self.code:
            self.code = self.get_code(self.discodes_id)

        return BaseModel.save(self)

    def getBindedNets(self):
        answer = []

        if not self.user_id:
            return answer

        tokens = SocToken.query.filter_by(
            user_id=self.user_id, write_access=1).all()

        for token in tokens:
            item = {'soc_id': token.type, 'name': token.netName()}
            answer.append(item)

        return answer
