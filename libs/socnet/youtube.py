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


class YouTubeApi(SocnetBase):

    API_PATH = 'https://www.googleapis.com/youtube/'
    TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    HISTORY_URL = 'https://gdata.youtube.com/feeds/api/users/default/watch_history?v=2'

    API_PARTS = {
        'subscriptions':
        'v3/subscriptions?maxResults=50&part=snippet&mine=true',
        'watch': 'watch?v=',
    }
    VIDEO_URLS = ['watch?v=', 'youtube.com/v/', '/videos/']

    def check_following(self, url, token_id, loyalty_id):
        follow = False
        self.refresh_token(token_id)
        soc_token = SocToken.query.get(token_id)
        action = PaymentLoyalty.query.get(loyalty_id)
        target = json.loads(action.data)

        g = Grab()
        g.setup(headers={'Authorization': 'Bearer ' + soc_token.user_token})
        url_api = self.API_PATH + self.API_PARTS['subscriptions']

        while not follow:
            g.go(url_api)
            subscriptions = json.loads(g.response.body)

            if 'items' not in subscriptions:
                break
            if len(subscriptions['items']) <= 0:
                break

            for subscribe in subscriptions['items']:
                if 'snippet' in subscribe and 'channelId' in subscribe['snippet'] and subscribe['snippet']['channelId'] == target['channelId']:
                    follow = True

            if 'nextPageToken' not in subscriptions:
                break
            if len(subscriptions['nextPageToken']) <= 0:
                break

            url_api = "%s%s&pageToken=%s" % (
                self.API_PATH,
                self.API_PARTS['subscriptions'],
                subscriptions['nextPageToken'])

        return follow

    def check_views(self, url, token_id, loyalty_id):
        viewed = False
        self.refresh_token(token_id)
        soc_token = SocToken.query.get(token_id)

        url = "%s&access_token=%s" % (self.HISTORY_URL, soc_token.user_token)
        watch_history = request_helper.make_request(url, False)
        target_id = self.parse_video_id(url)

        watch_history = unicode(watch_history, 'latin1')
        if '/' + target_id in watch_history or self.API_PARTS['watch'] + target_id in watch_history:
            viewed = True

        return viewed

    def refresh_token(self, token_id):
        soc_token = SocToken.query.get(token_id)
        if time.time() > soc_token.token_expires and len(soc_token.refresh_token) > 0:
            g = Grab()
            g.setup(
                post={
                    'client_id': SocConfig.GOOGLE_ID,
                    'client_secret': SocConfig.GOOGLE_SECRET,
                    'refresh_token': soc_token.refresh_token,
                    'grant_type': 'refresh_token'})
            g.go(self.TOKEN_URL)
            newToken = json.loads(g.response.body)

            if 'access_token' in newToken and 'expires_in' in newToken:
                soc_token.user_token = newToken['access_token']
                soc_token.token_expires = math.floor(time.time()) + newToken['expires_in'] - 60
                soc_token.save()

    def parse_video_id(self, url):
        video_id = url

        for video_url in self.VIDEO_URLS:
            if video_url not in url:
                break

            video_id = request_helper.parse_get_param(url, video_url)

        return video_id
