# -*- coding: utf-8 -*-
"""
    Библиотека для работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
#from libs.facebook_api import FacebookApi
from libs.mock_facebook_api import MockFacebookApi
from models.soc_token import SocToken


class SocnetsApi():

    @staticmethod
    def check_like(type, url, token):
        pageLiked = False

        if type == SocToken.TYPE_FACEBOOK:
            facebookApi = MockFacebookApi()
            pageLiked = facebookApi.check_like(url, token)

        return pageLiked
