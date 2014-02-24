# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest

import web
from helpers import hash_helper
from models.loyalty import Loyalty


class WebApiSocialTestCase(unittest.TestCase):

    LOYALTY_URL = '/api/social/loyalty'

    ADMIN_KEY = '7131b1e8722240660480dfbb99592cb030debfa9'
    ADMIN_SECRET = 'cb81b4036eb381e528062a582725b1ec4d91650664e78a26c30a8147'

    def setUp(self):
        self.app = web.app.test_client()

    def test_loyalty_list(self):
        data = {}
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.get(self.LOYALTY_URL, headers=headers)
        self.assertEqual(rv.status_code, 200)

    def test_loyalty_details(self):
        data = {}
        coupon = Loyalty.query.filter(Loyalty.coupon_class != None).first()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.get(
            self.LOYALTY_URL + '/' + str(coupon.id), headers=headers)
        self.assertEqual(rv.status_code, 200)
