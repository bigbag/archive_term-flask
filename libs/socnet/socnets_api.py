# -*- coding: utf-8 -*-
"""
    Библиотека для работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from models.loyalty import Loyalty
from libs.socnet.facebook import FacebookApi
from libs.socnet.twitter import TwitterApi
from libs.socnet.foursquare import FoursquareApi
from libs.socnet.instagram import InstagramApi
from libs.socnet.google import GoogleApi
from libs.socnet.youtube import YouTubeApi


class SocnetsApi():

    SHARING_TYPES = {
        Loyalty.FACEBOOK_LIKE: {'netClass': FacebookApi, 'sharingCheck': 'check_like'},
        Loyalty.FACEBOOK_SHARE: {'netClass': FacebookApi, 'sharingCheck': 'check_sharing'},
        Loyalty.TWITTER_SHARE: {'netClass': TwitterApi, 'sharingCheck': 'checkSharing'},
        Loyalty.TWITTER_RETWIT: {'netClass': TwitterApi, 'sharingCheck': 'checkRetwit'},
        Loyalty.TWITTER_READING: {'netClass': TwitterApi, 'sharingCheck': 'checkReading'},
        Loyalty.TWITTER_HASHTAG: {'netClass': TwitterApi, 'sharingCheck': 'checkHashtag'},
        Loyalty.FOURSQUARE_CHECKIN: {'netClass': FoursquareApi, 'sharingCheck': 'check_checkin'},
        Loyalty.FOURSQUARE_MAYOR: {'netClass': FoursquareApi, 'sharingCheck': 'check_mayor'},
        Loyalty.FOURSQUARE_BADGE: {'netClass': FoursquareApi, 'sharingCheck': 'check_badge'},
        Loyalty.INSTAGRAM_LIKE: {'netClass': InstagramApi, 'sharingCheck': 'check_like'},
        Loyalty.INSTAGRAM_FOLLOWING: {'netClass': InstagramApi, 'sharingCheck': 'check_following'},
        Loyalty.GOOGLE_CIRCLE: {'netClass': GoogleApi, 'sharingCheck': 'check_in_circle'},
        Loyalty.GOOGLE_PLUS_ONE: {'netClass': GoogleApi, 'sharingCheck': 'check_plus'},
        Loyalty.YOUTUBE_FOLLOWING: {'netClass': YouTubeApi, 'sharingCheck': 'check_following'},
        Loyalty.YOUTUBE_VIEWS: {'netClass': YouTubeApi, 'sharingCheck': 'check_views'},
    }

    def check_soc_sharing(self, type, url, token_id, loyalty_id):
        netShared = False

        socApi = self.SHARING_TYPES[type]['netClass']()
        method = getattr(socApi, self.SHARING_TYPES[type]['sharingCheck'])
        netShared = method(url, token_id, loyalty_id)

        return netShared
