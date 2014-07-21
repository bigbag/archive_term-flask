# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Instagram

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet.socnet_base import SocnetBase
from models.soc_token import SocToken
from models.payment_loyalty import PaymentLoyalty
from grab import Grab
import json
import urllib
import pprint
from helpers import request_helper


class InstagramApi(SocnetBase):

    API_PATH = 'https://api.instagram.com/v1/'
    API_PARTS = {
        'base': 'instagram.com/',
        'oembed': 'http://api.instagram.com/oembed?url=',
        'search_users': 'users/search?q=',
        'relationship': 'users/%s/relationship',
        'media_likes': 'media/%s/likes',
    }

    def check_like(self, url, token_id, loyalty_id):
        liked = False

        likes_data = self.get_media_likes(url, token_id)

        if 'data' in likes_data and len(likes_data['data']) > 0:
            soc_token = SocToken.query.get(token_id)
            for user in likes_data['data']:
                if 'id' in user and user['id'] == soc_token.soc_id:
                    liked = True

        return liked

    def check_following(self, url, token_id, loyalty_id):
        follow = False
        relation = self.get_relation(url, token_id)

        if 'data' in relation and 'outgoing_status' in relation['data'] and relation['data']['outgoing_status'] == 'follows':
            follow = True

        return follow

    def get_media_likes(self, url, token_id):
        likes_data = {}

        url = "%s%s" (self.API_PARTS['oembed'], url)
        post_meta = request_helper.make_request(url, True)
        if 'media_id' in post_meta:
            soc_token = SocToken.query.get(token_id)
            request_url = "%s%s?access_token=%s" % (
                self.API_PATH,
                self.API_PARTS['media_likes'] % (post_meta['media_id']),
                user_token)

            likes_data = request_helper.make_request(request_url, True)

        return likes_data

    def get_relation(self, url, token_id):
        relation = {}
        soc_token = SocToken.query.get(token_id)
        request_url = "%s%s%s&access_token=%s" % (
            self.API_PATH,
            self.API_PARTS['search_users'],
            request_helper.parse_get_param(url, self.API_PARTS['base']),
            soc_token.user_token
        )
        user = request_helper.make_request(request_url, True)
        if 'data' in user and len(user['data']) > 0 and 'id' in user['data'][0]:
            request_url = "%s%s?access_token=%s" % (
                self.API_PATH,
                self.API_PARTS['relationship'] % (user['data'][0]['id']),
                soc_token.user_token)
            relation = request_helper.make_request(request_url, True)

        return relation
