# -*- coding: utf-8 -*-
"""
    Тест интерфейса соцсетей

    :copyright: (c) 2014 by Amelin Denis.
    :license: BSD, see LICENSE for more details.
"""
import unittest
import web

from libs.socnet_api_base import SocnetApiBase
from libs.mock_facebook_api import MockFacebookApi
from libs.mock_twitter_api import MockTwitterApi


class SocnetsApiTestCase(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

    def test_facebook_liked(self):
        facebookApi = MockFacebookApi()
        self.assertEqual(facebookApi.check_like(
            'url', SocnetApiBase.TOKEN_FOR_SHARED), True)

    def test_facebook_not_liked(self):
        facebookApi = MockFacebookApi()
        self.assertEqual(facebookApi.check_like(
            'url', SocnetApiBase.TOKEN_NOT_SHARED), False)

    def test_twitter_retweted(self):
        twitterApi = MockTwitterApi()
        self.assertEqual(twitterApi.checkRetwit(
            'url', SocnetApiBase.TOKEN_FOR_SHARED), True)

    def test_twitter_not_retweeted(self):
        twitterApi = MockTwitterApi()
        self.assertEqual(twitterApi.checkRetwit(
            'url', SocnetApiBase.TOKEN_NOT_SHARED), False)

    def test_twitter_reading(self):
        twitterApi = MockTwitterApi()
        self.assertEqual(twitterApi.checkReading(
            'url', SocnetApiBase.TOKEN_FOR_SHARED), True)

    def test_twitter_not_reading(self):
        twitterApi = MockTwitterApi()
        self.assertEqual(twitterApi.checkReading(
            'url', SocnetApiBase.TOKEN_NOT_SHARED), False)

    def test_twitter_hahtag(self):
        twitterApi = MockTwitterApi()
        self.assertEqual(twitterApi.checkHashtag(
            'url', SocnetApiBase.TOKEN_FOR_SHARED), True)

    def test_twitter_without_hahtag(self):
        twitterApi = MockTwitterApi()
        self.assertEqual(twitterApi.checkHashtag(
            'url', SocnetApiBase.TOKEN_NOT_SHARED), False)
