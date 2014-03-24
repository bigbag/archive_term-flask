# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Facebook

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet.socnet_base import SocnetBase
from models.soc_token import SocToken
from grab import Grab
import json
import urllib
import pprint
from helpers import request_helper


class FacebookApi(SocnetBase):

    API_PATH = 'https://graph.facebook.com/'
    FQL_PATH = 'https://graph.facebook.com/fql?q='
    URLS_PARTS = {
        'base': 'facebook.com/',
        'photo': '/photo.php?fbid=',
        'posts': '/posts/',
        'my_likes': 'me/likes/',
    }

    def check_like(self, url, token_id, loyalty_id):
        pageLiked = False
        object_id = 0

        if self.URLS_PARTS['base'] in url and (self.URLS_PARTS['photo'] in url or self.URLS_PARTS['posts'] in url):
            if self.URLS_PARTS['posts'] in url:
                # пост
                object_id = request_helper.parse_get_param(
                    url, self.URLS_PARTS['posts'])
            else:
                # фото
                object_id = request_helper.parse_get_param(
                    url, self.URLS_PARTS['photo'])
            like = self.get_object_like(object_id, token_id, True)
            if 'data' in like and len(like['data']) > 0 \
                and 'object_id' in like['data'][0] \
                    and like['data'][0]['object_id'] == object_id:
                pageLiked = True
        elif self.URLS_PARTS['base'] in url:
            page = self.get_page(url, token_id, True)

            if page.get('id'):
                like = self.get_like(page['id'], token_id, True)

                if 'data' in like and len(like['data']) > 0 and like['data'][0].get('id'):
                    pageLiked = True
        else:
            # like внешней ссылки
            like = self.get_external_like(url, token_id)
            if 'data' in like and len(like['data']) > 0 \
                and 'attachment' in like['data'][0] \
                    and 'href' in like['data'][0]['attachment']:
                pageLiked = True

        return pageLiked

    def check_sharing(self, url, token_id, loyalty_id):
        urlShared = False

        sharing = self.get_sharing(url, token_id, True)
        if 'data' in sharing and len(sharing['data']) > 0 \
            and 'attachment' in sharing['data'][0] \
                and 'href' in sharing['data'][0]['attachment']:
            urlShared = True

        return urlShared

    @staticmethod
    def parse_username(url):
        username = url
        if FacebookApi.URLS_PARTS['base'] in username:
            username = username[
                username.find(FacebookApi.URLS_PARTS['base']) + len(FacebookApi.URLS_PARTS['base']):]

        username = request_helper.clear_get_params(username)

        return username

    def get_page(self, url, token_id, parse_json):
        socToken = SocToken.query.get(token_id)
        username = FacebookApi.parse_username(url)
        urlAPI = self.API_PATH + username + \
            '?access_token=' + socToken.user_token

        return request_helper.make_request(urlAPI, parse_json)

    def get_like(self, page_id, token_id, parse_json):
        socToken = SocToken.query.get(token_id)
        urlAPI = self.API_PATH + self.URLS_PARTS['my_likes'] + \
            page_id + '?access_token=' + socToken.user_token

        return request_helper.make_request(urlAPI, parse_json)

    def get_object_like(self, object_id, token_id, parse_json):
        socToken = SocToken.query.get(token_id)
        query = 'SELECT object_id,user_id FROM like WHERE user_id = me() and object_id = %s' % (
            object_id)

        return request_helper.make_request(self.FQL_PATH + query.replace(' ', '+') + '&access_token=' + socToken.user_token, parse_json)

    def get_external_like(self, url, token_id):
        socToken = SocToken.query.get(token_id)
        query = 'SELECT attachment ,created_time ,type ,description FROM stream WHERE source_id=me() and strpos(attachment.href,"%s")>=0 and strpos(attachment.href,"fb_action_types=og.likes") > 0' % (
            url)

        return request_helper.make_request(self.FQL_PATH + query.replace(' ', '+') + '&access_token=' + socToken.user_token, True)

    def get_sharing(self, url, token_id, parse_json):
        socToken = SocToken.query.get(token_id)
        query = 'SELECT attachment ,created_time ,type ,description FROM stream WHERE source_id=me() and actor_id=me() and type=80 and attachment.href="%s"' % (
            url)

        return request_helper.make_request(self.FQL_PATH + query.replace(' ', '+') + '&access_token=' + socToken.user_token, parse_json)
