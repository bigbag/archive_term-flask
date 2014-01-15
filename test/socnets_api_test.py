# -*- coding: utf-8 -*-
"""
    Тест интерфейса соцсетей

    :copyright: (c) 2014 by Amelin Denis.
    :license: BSD, see LICENSE for more details.
"""
import unittest
import web

from libs.mock_facebook_api import MockFacebookApi

class SocnetsApiTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = web.app.test_client()
        
    def test_facebook_liked(self):
        facebookApi = MockFacebookApi()
        self.assertEqual(facebookApi.check_like('url', MockFacebookApi.TOKEN_FOR_LIKED), True)
        
    def test_facebook_not_liked(self):
        facebookApi = MockFacebookApi()
        self.assertEqual(facebookApi.check_like('url', 'token'), False)
        
