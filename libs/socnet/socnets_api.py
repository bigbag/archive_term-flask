# -*- coding: utf-8 -*-
"""
    Библиотека для работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet.facebook import FacebookApi
from libs.socnet.twitter import TwitterApi
from libs.socnet.foursquare import FoursquareApi
from libs.socnet.instagram import InstagramApi
from libs.socnet.google import GoogleApi
from libs.socnet.youtube import YouTubeApi
from libs.socnet.vk import VkApi
from models.payment_loyalty import PaymentLoyalty
from models.payment_loyalty_sharing import PaymentLoyaltySharing
from models.soc_token import SocToken


class SocnetsApi():

    SHARING_TYPES = {
        PaymentLoyalty.FACEBOOK_LIKE: {'netClass': FacebookApi, 'sharingCheck': 'check_like', 'get_control_value': 'get_loyalty_likes', 'changing_control_value': True},
        PaymentLoyalty.FACEBOOK_SHARE: {'netClass': FacebookApi, 'sharingCheck': 'check_sharing', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.TWITTER_SHARE: {'netClass': TwitterApi, 'sharingCheck': 'checkSharing', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.TWITTER_RETWIT: {'netClass': TwitterApi, 'sharingCheck': 'checkRetwit', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.TWITTER_READING: {'netClass': TwitterApi, 'sharingCheck': 'checkReading', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.TWITTER_HASHTAG: {'netClass': TwitterApi, 'sharingCheck': 'checkHashtag', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.FOURSQUARE_CHECKIN: {'netClass': FoursquareApi, 'sharingCheck': 'check_checkin', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.FOURSQUARE_MAYOR: {'netClass': FoursquareApi, 'sharingCheck': 'check_mayor', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.FOURSQUARE_BADGE: {'netClass': FoursquareApi, 'sharingCheck': 'check_badge', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.INSTAGRAM_LIKE: {'netClass': InstagramApi, 'sharingCheck': 'check_like', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.INSTAGRAM_FOLLOWING: {'netClass': InstagramApi, 'sharingCheck': 'check_following', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.GOOGLE_CIRCLE: {'netClass': GoogleApi, 'sharingCheck': 'check_in_circle', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.GOOGLE_PLUS_ONE: {'netClass': GoogleApi, 'sharingCheck': 'check_plus', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.YOUTUBE_FOLLOWING: {'netClass': YouTubeApi, 'sharingCheck': 'check_following', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.YOUTUBE_VIEWS: {'netClass': YouTubeApi, 'sharingCheck': 'check_views', 'get_control_value': 'dummy_control', 'changing_control_value': False},
        PaymentLoyalty.VK_SUBS: {'netClass': VkApi, 'sharingCheck': 'check_subscription', 'get_control_value': 'subscription_control', 'changing_control_value': True},
    }

    TOKEN_TYPES = {
        PaymentLoyalty.FACEBOOK_LIKE: SocToken.TYPE_FACEBOOK,
        PaymentLoyalty.FACEBOOK_SHARE: SocToken.TYPE_FACEBOOK,
        PaymentLoyalty.TWITTER_SHARE: SocToken.TYPE_TWITTER,
        PaymentLoyalty.TWITTER_RETWIT: SocToken.TYPE_TWITTER,
        PaymentLoyalty.TWITTER_READING: SocToken.TYPE_TWITTER,
        PaymentLoyalty.TWITTER_HASHTAG: SocToken.TYPE_TWITTER,
        PaymentLoyalty.FOURSQUARE_CHECKIN: SocToken.TYPE_FOURSQUARE,
        PaymentLoyalty.FOURSQUARE_MAYOR: SocToken.TYPE_FOURSQUARE,
        PaymentLoyalty.FOURSQUARE_BADGE: SocToken.TYPE_FOURSQUARE,
        PaymentLoyalty.INSTAGRAM_LIKE: SocToken.TYPE_INSTAGRAM,
        PaymentLoyalty.INSTAGRAM_FOLLOWING: SocToken.TYPE_INSTAGRAM,
        PaymentLoyalty.GOOGLE_CIRCLE: SocToken.TYPE_GOOGLE,
        PaymentLoyalty.GOOGLE_PLUS_ONE: SocToken.TYPE_GOOGLE,
        PaymentLoyalty.YOUTUBE_FOLLOWING: SocToken.TYPE_YOUTUBE,
        PaymentLoyalty.YOUTUBE_VIEWS: SocToken.TYPE_YOUTUBE,
        PaymentLoyalty.VK_SUBS: SocToken.TYPE_VK,
    }

    def check_soc_sharing(self, type, url, token_id, sharing_id):
        netShared = False

        socApi = self.SHARING_TYPES[type]['netClass']()
        method = getattr(socApi, self.SHARING_TYPES[type]['sharingCheck'])
        netShared = method(url, token_id, sharing_id)

        return netShared

    def post_photo(self, type, token_id, filepath, message):
        # пока только facebook
        socApi = FacebookApi()

        return socApi.post_photo(token_id, filepath, message)

    def get_control_value(self, condition_id):
        """контрольное значение для условия акции"""
        answer = False
        condition = PaymentLoyaltySharing.query.get(condition_id)
        if not condition:
            return False

        type = condition.sharing_type

        socApi = self.SHARING_TYPES[type]['netClass']()
        method = getattr(socApi, self.SHARING_TYPES[type]['get_control_value'])
        answer = method(condition_id)

        return answer

    def need_control_value(self, condition_id):
        """опреляется ли контрольное значение для условия акции"""
        answer = False
        condition = PaymentLoyaltySharing.query.get(condition_id)
        if not condition:
            return False

        type = condition.sharing_type

        answer = self.SHARING_TYPES[type]['changing_control_value']

        return answer

    def get_token_type_by_sharing(self, sharing_type):

        return self.TOKEN_TYPES[sharing_type]
