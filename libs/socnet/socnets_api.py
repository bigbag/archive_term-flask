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
from models.payment_loyalty import PaymentLoyalty
from models.soc_token import SocToken


class SocnetsApi():

    SHARING_TYPES = {
        PaymentLoyalty.FACEBOOK_LIKE: {'netClass': FacebookApi, 'sharingCheck': 'check_like', 'get_control_value': 'get_loyalty_likes'},
        PaymentLoyalty.FACEBOOK_SHARE: {'netClass': FacebookApi, 'sharingCheck': 'check_sharing', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.TWITTER_SHARE: {'netClass': TwitterApi, 'sharingCheck': 'checkSharing', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.TWITTER_RETWIT: {'netClass': TwitterApi, 'sharingCheck': 'checkRetwit', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.TWITTER_READING: {'netClass': TwitterApi, 'sharingCheck': 'checkReading', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.TWITTER_HASHTAG: {'netClass': TwitterApi, 'sharingCheck': 'checkHashtag', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.FOURSQUARE_CHECKIN: {'netClass': FoursquareApi, 'sharingCheck': 'check_checkin', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.FOURSQUARE_MAYOR: {'netClass': FoursquareApi, 'sharingCheck': 'check_mayor', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.FOURSQUARE_BADGE: {'netClass': FoursquareApi, 'sharingCheck': 'check_badge', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.INSTAGRAM_LIKE: {'netClass': InstagramApi, 'sharingCheck': 'check_like', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.INSTAGRAM_FOLLOWING: {'netClass': InstagramApi, 'sharingCheck': 'check_following', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.GOOGLE_CIRCLE: {'netClass': GoogleApi, 'sharingCheck': 'check_in_circle', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.GOOGLE_PLUS_ONE: {'netClass': GoogleApi, 'sharingCheck': 'check_plus', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.YOUTUBE_FOLLOWING: {'netClass': YouTubeApi, 'sharingCheck': 'check_following', 'get_control_value': 'dummy_control'},
        PaymentLoyalty.YOUTUBE_VIEWS: {'netClass': YouTubeApi, 'sharingCheck': 'check_views', 'get_control_value': 'dummy_control'},
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
    }

    def check_soc_sharing(self, type, url, token_id, loyalty_id):
        netShared = False

        socApi = self.SHARING_TYPES[type]['netClass']()
        method = getattr(socApi, self.SHARING_TYPES[type]['sharingCheck'])
        netShared = method(url, token_id, loyalty_id)

        return netShared

    def post_photo(self, type, token_id, filepath, message):
        # пока только facebook
        socApi = FacebookApi()

        return socApi.post_photo(token_id, filepath, message)

    def get_control_value(self, loyalty_id):
        """контрольное значение для акции"""
        answer = False
        loyalty = PaymentLoyalty.query.get(loyalty_id)
        if not loyalty:
            return False

        type = loyalty.sharing_type

        socApi = self.SHARING_TYPES[type]['netClass']()
        method = getattr(socApi, self.SHARING_TYPES[type]['get_control_value'])
        answer = method(loyalty_id)

        return answer

    def get_token_type_by_sharing(self, sharing_type):

        return self.TOKEN_TYPES[sharing_type]
