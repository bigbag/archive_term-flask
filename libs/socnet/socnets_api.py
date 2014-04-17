# -*- coding: utf-8 -*-
"""
    Библиотека для работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from models.payment_loyalty import PaymentLoyalty
from libs.socnet.facebook import FacebookApi
from libs.socnet.twitter import TwitterApi
from libs.socnet.foursquare import FoursquareApi
from libs.socnet.instagram import InstagramApi
from libs.socnet.google import GoogleApi
from libs.socnet.youtube import YouTubeApi


class SocnetsApi():

    SHARING_TYPES = {
        PaymentLoyalty.FACEBOOK_LIKE: {'netClass': FacebookApi, 'sharingCheck': 'check_like'},
        PaymentLoyalty.FACEBOOK_SHARE: {'netClass': FacebookApi, 'sharingCheck': 'check_sharing'},
        PaymentLoyalty.TWITTER_SHARE: {'netClass': TwitterApi, 'sharingCheck': 'checkSharing'},
        PaymentLoyalty.TWITTER_RETWIT: {'netClass': TwitterApi, 'sharingCheck': 'checkRetwit'},
        PaymentLoyalty.TWITTER_READING: {'netClass': TwitterApi, 'sharingCheck': 'checkReading'},
        PaymentLoyalty.TWITTER_HASHTAG: {'netClass': TwitterApi, 'sharingCheck': 'checkHashtag'},
        PaymentLoyalty.FOURSQUARE_CHECKIN: {'netClass': FoursquareApi, 'sharingCheck': 'check_checkin'},
        PaymentLoyalty.FOURSQUARE_MAYOR: {'netClass': FoursquareApi, 'sharingCheck': 'check_mayor'},
        PaymentLoyalty.FOURSQUARE_BADGE: {'netClass': FoursquareApi, 'sharingCheck': 'check_badge'},
        PaymentLoyalty.INSTAGRAM_LIKE: {'netClass': InstagramApi, 'sharingCheck': 'check_like'},
        PaymentLoyalty.INSTAGRAM_FOLLOWING: {'netClass': InstagramApi, 'sharingCheck': 'check_following'},
        PaymentLoyalty.GOOGLE_CIRCLE: {'netClass': GoogleApi, 'sharingCheck': 'check_in_circle'},
        PaymentLoyalty.GOOGLE_PLUS_ONE: {'netClass': GoogleApi, 'sharingCheck': 'check_plus'},
        PaymentLoyalty.YOUTUBE_FOLLOWING: {'netClass': YouTubeApi, 'sharingCheck': 'check_following'},
        PaymentLoyalty.YOUTUBE_VIEWS: {'netClass': YouTubeApi, 'sharingCheck': 'check_views'},
    }

    def check_soc_sharing(self, type, url, token_id, loyalty_id):
        netShared = False

        socApi = self.SHARING_TYPES[type]['netClass']()
        method = getattr(socApi, self.SHARING_TYPES[type]['sharingCheck'])
        netShared = method(url, token_id, loyalty_id)

        return netShared
