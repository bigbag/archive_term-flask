# -*- coding: utf-8 -*-
"""
    Библиотека для работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.facebook_api import FacebookApi
from libs.mock_facebook_api import MockFacebookApi
from libs.twitter_api import TwitterApi
from libs.mock_twitter_api import MockTwitterApi
from models.loyalty import Loyalty


class SocnetsApi():

    @staticmethod
    def check_soc_sharing(type, url, token_id):
        netShared = False

        if type == Loyalty.FACEBOOK_LIKE:
            facebookApi = FacebookApi()
            netShared = facebookApi.check_like(url, token_id)
        elif type == Loyalty.TWITTER_SHARE:
            twitterApi = TwitterApi()
            netShared = twitterApi.checkSharing(url, token_id)
        elif type == Loyalty.TWITTER_RETWIT:
            twitterApi = TwitterApi()
            netShared = twitterApi.checkRetwit(url, token_id)
        elif type == Loyalty.TWITTER_READING:
            twitterApi = TwitterApi()
            netShared = twitterApi.checkReading(url, token_id)
        elif type == Loyalty.TWITTER_HASHTAG:
            twitterApi = TwitterApi()
            netShared = twitterApi.checkHashtag(url, token_id)

        return netShared
