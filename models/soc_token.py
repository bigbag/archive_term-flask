# -*- coding: utf-8 -*-
"""
    Модель для жетонов соцсетей

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class SocToken(db.Model, BaseModel):

    __bind_key__ = 'mobispot'
    __tablename__ = 'soc_token'

    TYPE_GOOGLE = 0
    TYPE_FACEBOOK = 1
    TYPE_TWITTER = 2
    TYPE_YOUTUBE = 3
    TYPE_DEVIANTART = 4
    TYPE_BEHANCE = 5
    TYPE_VIMEO = 6
    TYPE_VK = 7
    TYPE_FOURSQUARE = 8
    TYPE_LINKEDIN = 9
    TYPE_INSTAGRAM = 10

    SOC_NET = {
        TYPE_GOOGLE: 'google_oauth',
        TYPE_FACEBOOK: 'facebook',
        TYPE_TWITTER: 'twitter',
        TYPE_YOUTUBE: 'youtube',
        TYPE_DEVIANTART: 'deviantart',
        TYPE_BEHANCE: 'behance',
        TYPE_VIMEO: 'vimeo',
        TYPE_VK: 'vk',
        TYPE_FOURSQUARE: 'foursquare',
        TYPE_LINKEDIN: 'linkedin',
        TYPE_INSTAGRAM: 'instagram',
    }

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer)
    soc_id = db.Column(db.Integer)
    soc_username = db.Column(db.String(128))
    soc_email = db.Column(db.String(512))
    user_token = db.Column(db.String(512))
    token_secret = db.Column(db.String(512))
    token_expires = db.Column(db.Integer)
    is_tech = db.Column(db.Integer)
    allow_login = db.Column(db.Integer)
    refresh_token = db.Column(db.String(1024))
    write_access = db.Column(db.Integer)

    def netName(self):
        if not self.type:
            return False

        return self.SOC_NET[self.type]
