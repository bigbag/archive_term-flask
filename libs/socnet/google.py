# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Google+

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet.socnet_base import SocnetBase
from configs.soc_config import SocConfig
from models.soc_token import SocToken
from models.payment_loyalty import PaymentLoyalty
from grab import Grab
import json
import time
import math
from helpers import request_helper


class GoogleApi(SocnetBase):

    API_PATH = 'https://www.googleapis.com/plus/v1/'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    URLS_PARTS = {
        'base': 'google.com/',
        'plus': 'plus.google.com/',
        'user': 'google.com/u/0/',
    }
    API_PARTS = {
        'plusoners': '/people/plusoners?maxResults=100',
        'activities': 'activities/',
        'people_list': 'people/',
        'peoples': 'people/me/people/visible?maxResults=100',
    }

    def check_in_circle(self, url, token_id, loyalty_id):
        in_circle = False
        self.refresh_token(token_id)

        soc_token = SocToken.query.get(token_id)
        username = self.parse_username(url)
        request_url = "%s%s%s?key=%s" % (
            self.API_PATH,
            self.API_PARTS['people_list'],
            username,
            SocConfig.GOOGLE_KEY)
        taget_user = request_helper.make_request(request_url, True)

        if 'id' in taget_user and taget_user['id']:
            user_id = taget_user['id']
            g = Grab()
            g.setup(headers={'Authorization': 'Bearer ' + soc_token.user_token})

            url_api = self.API_PATH + self.API_PARTS['peoples']

            while not in_circle:
                g.go(url_api)
                circle = json.loads(g.response.body)

                if 'items' not in circle:
                    break
                if len(circle['items']) <= 0:
                    break

                for friend in circle['items']:
                    if 'id' in friend and friend['id'] == user_id:
                        in_circle = True

                if 'nextPageToken' not in circle:
                    break
                if len(circle['nextPageToken']) <= 0:
                    break

                url_api = "%s%s&pageToken=%s" % (
                    self.API_PATH,
                    self.API_PARTS['peoples'],
                    circle['nextPageToken'])

        return in_circle

    def check_plus(self, url, token_id, loyalty_id):
        plused = False
        self.refresh_token(token_id)

        action = PaymentLoyalty.query.get(loyalty_id)
        target = json.loads(action.data)
        soc_token = SocToken.query.get(token_id)
        g = Grab()
        # g.setup(headers={'Authorization':'Bearer ' + soc_token.user_token})
        url_api = "%s%s%s%s&key=%s" % (
            self.API_PATH,
            self.API_PARTS['activities'],
            target['id'],
            self.API_PARTS['plusoners'],
            SocConfig.GOOGLE_KEY)

        while not plused:
            g.go(url_api)
            plusoners = json.loads(g.response.body)

            if 'items' not in plusoners:
                break
            if len(plusoners['items']) <= 0:
                break

            for person in plusoners['items']:
                if 'id' in person and person['id'] == soc_token.soc_id:
                    plused = True

            if 'nextPageToken' in plusoners:
                break
            if len(plusoners['nextPageToken']) <= 0:
                break

            url_api = "%s%s%s%s&pageToken=%s&key=%s" % (
                self.API_PATH,
                self.API_PARTS['activities'],
                target['id'],
                self.API_PARTS['plusoners'],
                plusoners['nextPageToken'],
                SocConfig.GOOGLE_KEY)

        return plused

    def refresh_token(self, token_id):
        soc_token = SocToken.query.get(token_id)
        if time.time() > soc_token.token_expires and len(soc_token.refresh_token) > 0:
            g = Grab()
            g.setup(
                post={
                    'client_id': SocConfig.GOOGLE_ID,
                    'client_secret': SocConfig.GOOGLE_SECRET,
                    'refresh_token': soc_token.refresh_token, 'grant_type': 'refresh_token'})
            g.go(self.TOKEN_URL)
            newToken = json.loads(g.response.body)

            if 'access_token' in newToken and 'expires_in' in newToken:
                soc_token.user_token = newToken['access_token']
                soc_token.token_expires = math.floor(
                    time.time()) + newToken['expires_in'] - 60
                soc_token.save()

    def parse_username(self, url):
        user_id = url
        if self.URLS_PARTS['user'] in url:
            user_id = request_helper.parse_get_param(
                url, self.URLS_PARTS['user'])
        elif self.URLS_PARTS['plus'] in url:
            user_id = request_helper.parse_get_param(
                url, self.URLS_PARTS['plus'])
        elif self.URLS_PARTS['base'] in url:
            user_id = request_helper.parse_get_param(url, self.URLS_PARTS['base'])

        return user_id
