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
from libs.foursquare_api import FoursquareApi
from libs.instagram_api import InstagramApi
from libs.google_api import GoogleApi
from models.loyalty import Loyalty


class SocnetsApi():

    @staticmethod
    def check_soc_sharing(type, url, token_id, loyalty_id):
        netShared = False

        if type == Loyalty.FACEBOOK_LIKE:
            facebookApi = FacebookApi()
            netShared = facebookApi.check_like(url, token_id)
        elif type == Loyalty.FACEBOOK_SHARE:
            facebookApi = FacebookApi()
            netShared = facebookApi.check_sharing(url, token_id)
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
        elif type == Loyalty.FOURSQUARE_CHECKIN:
            fsqApi = FoursquareApi()
            netShared = fsqApi.check_checkin(url, token_id, loyalty_id)
        elif type == Loyalty.FOURSQUARE_MAYOR:
            fsqApi = FoursquareApi()
            netShared = fsqApi.check_mayor(url, token_id, loyalty_id)
        elif type == Loyalty.FOURSQUARE_BADGE:
            fsqApi = FoursquareApi()
            netShared = fsqApi.check_badge(url, token_id, loyalty_id)
        elif type == Loyalty.INSTAGRAM_LIKE:
            instApi = InstagramApi()
            netShared = instApi.check_like(url, token_id)
        elif type == Loyalty.INSTAGRAM_FOLLOWING:
            instApi = InstagramApi()
            netShared = instApi.check_following(url, token_id)
        elif type == Loyalty.GOOGLE_CIRCLE:
            gApi = GoogleApi()
            netShared = gApi.check_in_circle(url, token_id, loyalty_id)
        elif type == Loyalty.GOOGLE_PLUS_ONE:
            gApi = GoogleApi()
            netShared = gApi.check_plus(url, token_id, loyalty_id)

        return netShared
