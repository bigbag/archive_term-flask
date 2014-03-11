# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Google+

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet.socnet_base import SocnetBase
from configs.soc_config import SocConfig
from models.soc_token import SocToken
from models.loyalty import Loyalty
from grab import Grab
import json
import urllib
import pprint
import time
import math


class GoogleApi(SocnetBase):

    API_PATH = 'https://www.googleapis.com/plus/v1/'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

    def check_in_circle(self, url, token_id, loyalty_id):
        in_circle = False
        self.refresh_token(token_id)

        socToken = SocToken.query.get(token_id)
        username = self.parse_username(url)
        tagetUser = self.make_request(
            self.API_PATH + 'people/' + username + '?key=' + SocConfig.GOOGLE_KEY, True)

        if 'id' in tagetUser and tagetUser['id']:
            userId = tagetUser['id']
            g = Grab()
            g.setup(headers={'Authorization': 'Bearer ' + socToken.user_token})

            urlApi = self.API_PATH + 'people/me/people/visible?maxResults=100'

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
                        'people/me/people/visible?maxResults=100&pageToken=' + \
                        circle['nextPageToken']
                else:
                    break

        return in_circle

    def check_plus(self, url, token_id, loyalty_id):
        plused = False
        self.refresh_token(token_id)

        action = Loyalty.query.get(loyalty_id)
        target = json.loads(action.data)
        socToken = SocToken.query.get(token_id)
        g = Grab()
        # g.setup(headers={'Authorization':'Bearer ' + socToken.user_token})
        urlApi = self.API_PATH + 'activities/' + \
            target['id'] + '/people/plusoners?maxResults=100&key=' + \
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
                    urlApi = self.API_PATH + 'activities/' + \
                        target['id'] + '/people/plusoners?maxResults=100&pageToken=' + plusoners[
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

    def get_circle(self, token_id, pageToken):
        socToken = SocToken.query.get(token_id)

    def parse_username(self, url):
        userId = url
        if 'google.com/u/0/' in url:
            userId = self.parse_get_param(url, 'google.com/u/0/')
        elif 'plus.google.com/' in url:
            userId = self.parse_get_param(url, 'plus.google.com/')
        elif 'google.com/' in url:
            userId = self.parse_get_param(url, 'google.com/')

        return userId
