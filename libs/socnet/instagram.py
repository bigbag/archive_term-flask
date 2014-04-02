# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Instagram

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet.socnet_base import SocnetBase
from models.soc_token import SocToken
from models.loyalty import Loyalty
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

        likesData = self.get_media_likes(url, token_id)

        if 'data' in likesData and len(likesData['data']) > 0:
            socToken = SocToken.query.get(token_id)
            for user in likesData['data']:
                if 'id' in user and user['id'] == socToken.soc_id:
                    liked = True

        return liked

    def check_following(self, url, token_id, loyalty_id):
        follow = False
        relation = self.get_relation(url, token_id)

        if 'data' in relation and 'outgoing_status' in relation['data'] and relation['data']['outgoing_status'] == 'follows':
            follow = True

        return follow

    def get_media_likes(self, url, token_id):
        likesData = {}

        postMeta = request_helper.make_request(
            self.API_PARTS['oembed'] + url, True)
        if 'media_id' in postMeta:
            socToken = SocToken.query.get(token_id)
            likesData = request_helper.make_request(self.API_PATH + self.API_PARTS['media_likes'] % (postMeta[
                                                    'media_id']) + '?access_token=' + socToken.user_token, True)

        return likesData

    def get_relation(self, url, token_id):
        relation = {}
        socToken = SocToken.query.get(token_id)

        user = request_helper.make_request(self.API_PATH + self.API_PARTS['search_users'] + request_helper.parse_get_param(
            url, self.API_PARTS['base']) + '&access_token=' + socToken.user_token, True)
        if 'data' in user and len(user['data']) > 0 and 'id' in user['data'][0]:
            relation = request_helper.make_request(self.API_PATH + self.API_PARTS[
                                                   'relationship'] % (user['data'][0]['id']) + '?access_token=' + socToken.user_token, True)

        return relation
