# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Facebook

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from grab import Grab
import json


class FacebookApi():

    @staticmethod
    def check_like(url, token):
        pageLiked = False
        username = FacebookApi.parse_username(url)
        urlAPI = 'https://graph.facebook.com/' + \
            username + '?access_token=' + token
        g = Grab()
        g.go(urlAPI)
        page = json.loads(g.response.body)

        if page.get('id'):
            urlAPI = 'https://graph.facebook.com/me/likes/' + \
                page['id'] + '?&access_token=' + token
            g.go(urlAPI)
            like = json.loads(g.response.body)

            if like.has_key('data') and len(like['data']) and like['data'][0].get('id'):
                pageLiked = True

        return pageLiked

    @staticmethod
    def parse_username(url):
        username = url
        if "facebook.com/" in username:
            username = username[
                username.find("facebook.com/") + len("facebook.com/"):]
        if "/" in username:
            username = username[0:username.find("/")]
        if "?" in username:
            username = username[0:username.find("?")]
        if "&" in username:
            username = username[0:username.find("&")]

        return username
