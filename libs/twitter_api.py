# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Twitter

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.soc_config import SocConfig
from libs.socnet_api_base import SocnetApiBase
from models.soc_token import SocToken
from grab import Grab
from twython import Twython
import json
import urllib

import pprint


class TwitterApi(SocnetApiBase):

    def checkSharing(self, url, token_id):
        shared = False
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        timeline = twitter.get_user_timeline(count=1)

        return shared

    def checkRetwit(self, url, token_id):
        retwitted = False
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        status_id = self.parse_status_id(url)
        twit = twitter.show_status(
            id=status_id, include_my_retweet='true', include_entities='false')

        if twit.has_key('current_user_retweet') and twit['current_user_retweet'].has_key('id') and twit['current_user_retweet']['id']:
            retwitted = True

        return retwitted

    def checkReading(self, url, token_id):
        reading = False
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        reading_name = self.parse_screen_name(url)
        friendship = twitter.lookup_friendships(screen_name=reading_name)

        if friendship[0].has_key('connections') and 'following' in friendship[0]['connections']:
            reading = True

        return reading

    def checkHashtag(self, url, token_id):
        posted = False
        hashtag = '#' + SocnetApiBase.parse_get_param(url, '#')
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        user = twitter.show_user(user_id=socToken.soc_id)
        if user.has_key('screen_name'):
            params = {'q': hashtag, 'count': 1, 'from': user['screen_name']}
            searchResult = twitter.get('search/tweets', params=params)
            if searchResult.has_key('statuses') and len(searchResult['statuses']):
                posted = True

        return posted

    @staticmethod
    def parse_screen_name(url):
        return SocnetApiBase.parse_get_param(url, 'https://twitter.com/')

    @staticmethod
    def parse_status_id(url):
        return SocnetApiBase.parse_get_param(url, '/status/')
