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
import urllib
import pprint
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

        socToken = SocToken.query.get(token_id)
        username = self.parse_username(url)
        tagetUser = request_helper.make_request(
            self.API_PATH + self.API_PARTS['people_list'] + username + '?key=' + SocConfig.GOOGLE_KEY, True)

        if 'id' in tagetUser and tagetUser['id']:
            userId = tagetUser['id']
            g = Grab()
            g.setup(headers={'Authorization': 'Bearer ' + socToken.user_token})

            urlApi = self.API_PATH + self.API_PARTS['peoples']

            while not in_circle:
                g.go(urlApi)
                circle = json.loads(g.response.body)

                if 'items' in circle and len(circle['items']) > 0:
                    for friend in circle['items']:
                        if 'id' in friend and friend['id'] == userId:
                            in_circle = True
                else:
                    break

                if 'nextPageToken' in circle and len(circle['nextPageToken']) > 0:
                    urlApi = self.API_PATH + \
                        self.API_PARTS['peoples'] + '&pageToken=' + \
                        circle['nextPageToken']
                else:
                    break

        return in_circle

    def check_plus(self, url, token_id, loyalty_id):
        plused = False
        self.refresh_token(token_id)

        action = PaymentLoyalty.query.get(loyalty_id)
        target = json.loads(action.data)
        socToken = SocToken.query.get(token_id)
        g = Grab()
        # g.setup(headers={'Authorization':'Bearer ' + socToken.user_token})
        urlApi = self.API_PATH + self.API_PARTS['activities'] + \
            target['id'] + self.API_PARTS['plusoners'] + '&key=' + \
            SocConfig.GOOGLE_KEY

        while not plused:

            g.go(urlApi)
            plusoners = json.loads(g.response.body)

            if 'items' in plusoners and len(plusoners['items']) > 0:
                for person in plusoners['items']:
                    if 'id' in person and person['id'] == socToken.soc_id:
                        plused = True
            else:
                break

            if 'nextPageToken' in plusoners and len(plusoners['nextPageToken']) > 0:
                    urlApi = self.API_PATH + self.API_PARTS['activities'] + \
                        target['id'] + self.API_PARTS['plusoners'] + '&pageToken=' + plusoners[
                            'nextPageToken'] + '&key=' + SocConfig.GOOGLE_KEY
            else:
                break

        return plused

    def refresh_token(self, token_id):
        socToken = SocToken.query.get(token_id)
        if time.time() > socToken.token_expires and len(socToken.refresh_token) > 0:
            g = Grab()
            g.setup(
                post={
                    'client_id': SocConfig.GOOGLE_ID,
                    'client_secret': SocConfig.GOOGLE_SECRET,
                    'refresh_token': socToken.refresh_token, 'grant_type': 'refresh_token'})
            g.go(self.TOKEN_URL)
            newToken = json.loads(g.response.body)

            if 'access_token' in newToken and 'expires_in' in newToken:
                socToken.user_token = newToken['access_token']
                socToken.token_expires = math.floor(
                    time.time()) + newToken['expires_in'] - 60
                socToken.save()

    def parse_username(self, url):
        userId = url
        if self.URLS_PARTS['user'] in url:
            userId = request_helper.parse_get_param(
                url, self.URLS_PARTS['user'])
        elif self.URLS_PARTS['plus'] in url:
            userId = request_helper.parse_get_param(
                url, self.URLS_PARTS['plus'])
        elif self.URLS_PARTS['base'] in url:
            userId = request_helper.parse_get_param(
                url, self.URLS_PARTS['base'])

        return userId
