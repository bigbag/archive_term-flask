# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Facebook

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet_api_base import SocnetApiBase
from models.soc_token import SocToken
from grab import Grab
import json


class FacebookApi(SocnetApiBase):

    API_PATH = 'https://graph.facebook.com/'

    def check_like(self, url, token_id):
        pageLiked = False

        page = self.get_page(url, token_id, True)

        if page.get('id'):
            like = self.get_like(page['id'], token_id, True)

            if like.has_key('data') and len(like['data']) and like['data'][0].get('id'):
                pageLiked = True

        return pageLiked

    @staticmethod
    def parse_username(url):
        username = url
        if "facebook.com/" in username:
            username = username[
                username.find("facebook.com/") + len("facebook.com/"):]

        username = SocnetApiBase.rmGetParams(username)

        return username

    def get_page(self, url, token_id, parse_json):
        socToken = SocToken.query.get(token_id)
        username = FacebookApi.parse_username(url)
        urlAPI = self.API_PATH + username + \
            '?access_token=' + socToken.user_token

        return self.make_api_request(urlAPI, parse_json)

    def get_like(self, page_id, token_id, parse_json):
        socToken = SocToken.query.get(token_id)
        urlAPI = self.API_PATH + 'me/likes/' + \
            page_id + '?&access_token=' + socToken.user_token

        return self.make_api_request(urlAPI, parse_json)

    @staticmethod
    def make_api_request(url, parse_json):
        g = Grab()
        g.go(url)
        answer = g.response.body
        if parse_json:
            answer = json.loads(answer)

        return answer
