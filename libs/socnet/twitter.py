# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Twitter

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""

from configs.soc_config import SocConfig
from libs.socnet.socnet_base import SocnetBase
from models.soc_token import SocToken
from grab import Grab
from twython import Twython
from helpers import request_helper


class TwitterApi(SocnetBase):

    def checkSharing(self, url, token_id, loyalty_id):
        # пока решено отказаться от акций такого типа, это заготовка
        shared = False
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        # params = {'q': urllib.quote_plus(url), 'count': 1, 'from': socToken.soc_username}
        # searchResult = twitter.get('search/tweets', params=params)

        searchResult = twitter.get_user_timeline(
            user_id=socToken.soc_id, count=1)

        return shared

    def checkRetwit(self, url, token_id, loyalty_id):
        retwitted = False
        twit = self.get_tweet(token_id, url)

        if 'current_user_retweet' in twit and 'id' in twit['current_user_retweet'] and twit['current_user_retweet']['id']:
            retwitted = True

        return retwitted

    def checkReading(self, url, token_id, loyalty_id):
        reading = False

        friendship = self.get_friendship(token_id, url)

        if 'relationship' in friendship and 'source' in friendship['relationship'] and 'following' in friendship['relationship']['source'] and friendship['relationship']['source']['following']:
            reading = True

        return reading

    def checkHashtag(self, url, token_id, loyalty_id):
        posted = False

        searchHashtag = self.search_hashtag(token_id, url)

        if 'statuses' in searchHashtag and len(searchHashtag['statuses']):
            posted = True

        return posted

    @staticmethod
    def get_tweet(token_id, url):
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        status_id = TwitterApi.parse_status_id(url)
        tweet = twitter.show_status(
            id=status_id, include_my_retweet='true', include_entities='false')

        return tweet

    @staticmethod
    def get_friendship(token_id, url):
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)
        reading_name = TwitterApi.parse_screen_name(url)
        friendship = twitter.show_friendship(
            source_screen_name=socToken.soc_username, target_screen_name=reading_name)

        return friendship

    @staticmethod
    def search_hashtag(token_id, url):
        hashtag = '#' + request_helper.parse_get_param(url, '#')
        socToken = SocToken.query.get(token_id)
        twitter = Twython(
            SocConfig.TWITTER_KEY, SocConfig.TWITTER_SECRET, socToken.user_token, socToken.token_secret)

        params = {'q': hashtag, 'count': 1, 'from': socToken.soc_username}
        searchHashtag = twitter.get('search/tweets', params=params)

        return searchHashtag

    @staticmethod
    def parse_screen_name(url):
        return request_helper.parse_get_param(url, 'https://twitter.com/')

    @staticmethod
    def parse_status_id(url):
        return request_helper.parse_get_param(url, '/status/')
