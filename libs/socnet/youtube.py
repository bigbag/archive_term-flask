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


class YouTubeApi(SocnetBase):

    API_PATH = 'https://www.googleapis.com/youtube/'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'

    def check_following(self, url, token_id, loyalty_id):
        follow = False
        self.refresh_token(token_id)
        socToken = SocToken.query.get(token_id)
        action = Loyalty.query.get(loyalty_id)
        target = json.loads(action.data)

        g = Grab()
        g.setup(headers={'Authorization': 'Bearer ' + socToken.user_token})
        urlApi = self.API_PATH + \
            'v3/subscriptions?maxResults=50&part=snippet&mine=true'

        while not follow:
            g.go(urlApi)
            subscriptions = json.loads(g.response.body)

            if 'items' in subscriptions and len(subscriptions['items']) > 0:
                for subscribe in subscriptions['items']:
                    if 'snippet' in subscribe and 'channelId' in subscribe['snippet'] and subscribe['snippet']['channelId'] == target['channelId']:
                        follow = True
            else:
                break

            if 'nextPageToken' in subscriptions and len(subscriptions['nextPageToken']) > 0:
                    urlApi = self.API_PATH + \
                        'v3/subscriptions?maxResults=50&part=snippet&mine=true'
            else:
                break

        return follow

    def check_views(self, url, token_id, loyalty_id):
        viewed = False
        self.refresh_token(token_id)
        socToken = SocToken.query.get(token_id)

        watchHistory = self.make_request(
            'https://gdata.youtube.com/feeds/api/users/default/watch_history?v=2&access_token=' + socToken.user_token, False)
        targetId = self.parse_video_id(url)

        watchHistory = unicode(watchHistory, 'latin1')
        if '/' + targetId in watchHistory or 'watch?v=' + targetId in watchHistory:
            viewed = True

        return viewed

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

    def parse_video_id(self, url):
        videoId = url

        if 'watch?v=' in url:
            videoId = self.parse_get_param(url, 'watch?v=')
        elif 'youtube.com/v/' in url:
            videoId = self.parse_get_param(url, 'youtube.com/v/')
        elif '/videos/' in url:
            videoId = self.parse_get_param(url, '/videos/')

        return videoId
