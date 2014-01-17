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


class FacebookApi():

    def check_like(self, url, token_id):
        pageLiked = False
        socToken = SocToken.query.get(token_id)
        page = self.get_page(url, socToken.user_token, True)

        if page.get('id'):
            like = self.get_like(page['id'], socToken.user_token, True)

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

    def get_page(self, url, token, parse_json):
        username = FacebookApi.parse_username(url)
        urlAPI = 'https://graph.facebook.com/' + \
            username + '?access_token=' + token
        g = Grab()
        g.go(urlAPI)
        answer = g.response.body
        if parse_json:
            answer = json.loads(answer)

        return answer

    def get_like(self, page_id, token, parse_json):
        urlAPI = 'https://graph.facebook.com/me/likes/' + \
            page_id + '?&access_token=' + token
        g = Grab()
        g.go(urlAPI)
        answer = g.response.body
        if parse_json:
            answer = json.loads(answer)

        return answer
