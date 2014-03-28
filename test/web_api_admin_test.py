# -*- coding: utf-8 -*-
"""
    Тест веб интерфейса

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import unittest
import random
from lxml import etree

import web
from helpers import hash_helper

from models.payment_wallet import PaymentWallet
from models.spot import Spot


class WebApiAdminTestCase(unittest.TestCase):

    GENERATE_URL = '/api/admin/spot/generate'
    LINKING_URL = '/api/admin/spot/linking'
    FREE_URL = '/api/admin/spot/free'
    DELETE_URL = '/api/admin/spot/delete'
    INFO_URL = '/api/admin/spot'

    ADMIN_KEY = '7131b1e8722240660480dfbb99592cb030debfa9'
    FALED_KEY = '34454'
    ADMIN_SECRET = 'cb81b4036eb381e528062a582725b1ec4d91650664e78a26c30a8147'

    @staticmethod
    def valid_xml(data):
        result = False
        try:
            tree = etree.ElementTree(etree.XML(data))
        except Exception as e:
            print e
        else:
            result = True
        return result

    def setUp(self):
        self.app = web.app.test_client()
        self.spot = Spot.query.filter_by(status=Spot.STATUS_GENERATED).first()
        self.data = dict(count=1)
        self.random_hid = random.randint(100000000, 999999999)

    def test_auth(self):

        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, self.data)
        headers = [
            ('Key', self.FALED_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.GENERATE_URL, headers=headers, data=self.data)
        self.assertEqual(rv.status_code, 403)

    def test_spot_generate(self):
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, self.data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.GENERATE_URL, headers=headers, data=self.data)

        self.assertEqual(rv.status_code, 200)
        assert self.valid_xml(rv.data)

    def test_spot_generate_metod(self):
        rv = self.app.get(self.GENERATE_URL, data=self.data)
        self.assertEqual(rv.status_code, 405)

    def test_spot_generate_faled_request(self):
        data = dict(
            count='erete',
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.GENERATE_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 405)

    def test_spot_generate_max_count(self):
        data = dict(
            count=100,
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.GENERATE_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 200)
        assert self.valid_xml(rv.data)

    def test_spot_linking(self):

        data = dict(
            hid=self.random_hid,
            pids=self.random_hid,
            ean=self.spot.barcode
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)

        self.assertEqual(rv.status_code, 200)
        assert self.valid_xml(rv.data)

    def test_spot_linking_faled_request(self):

        data = dict(
            pids=self.random_hid,
            ean=self.spot.barcode
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 400)

    def test_spot_linking_not_found_spot(self):

        data = dict(
            hid=self.random_hid,
            pids=self.random_hid,
            ean='0011111111111'
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 404)

    def test_spot_linking_faled_ean(self):

        data = dict(
            hid=self.random_hid,
            pids=self.random_hid,
            ean='12323'
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 400)

    def test_spot_linking_faled_pids(self):

        data = dict(
            hid=self.random_hid,
            pids='sdouwerhwo',
            ean=self.spot.barcode
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 405)

    def test_spot_linking_foreign_wallet(self):
        wallet = PaymentWallet.query.filter(
            PaymentWallet.discodes_id != self.spot.discodes_id).first()

        data = dict(
            hid=wallet.hard_id,
            pids=self.random_hid,
            ean=self.spot.barcode
        )
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.post(self.LINKING_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 400)

    def test_spot_free(self):
        data = dict()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        rv = self.app.get(self.FREE_URL, headers=headers, data=data)

        self.assertEqual(rv.status_code, 200)
        assert self.valid_xml(rv.data)

    def test_spot_info_by_ean(self):

        data = dict()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        url = "%s/ean/%s" % (self.INFO_URL, self.spot.barcode)

        rv = self.app.get(url, headers=headers)

        self.assertEqual(rv.status_code, 200)
        assert self.valid_xml(rv.data)

    def test_spot_info_faled_ean(self):

        data = dict()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        url = "%s/ean/%s" % (self.INFO_URL, '1234567890123')

        rv = self.app.get(url, headers=headers)

        self.assertEqual(rv.status_code, 404)

    def test_spot_info_by_hid(self):

        data = dict()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        wallet = PaymentWallet.query.first()
        url = "%s/hid/%s" % (self.INFO_URL, wallet.hard_id)

        rv = self.app.get(url, headers=headers)
        self.assertEqual(rv.status_code, 200)
        assert self.valid_xml(rv.data)

    def test_spot_info_faled_hid(self):

        data = dict()
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)
        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]
        url = "%s/hid/%s" % (self.INFO_URL, 'rwewertwrgsrg')

        rv = self.app.get(url, headers=headers)
        self.assertEqual(rv.status_code, 404)

    def test_spot_delete(self):
        wallet = PaymentWallet.query.filter_by(
            user_id=0).first()

        data = dict(hid=wallet.hard_id)
        sign = hash_helper.get_api_sign(self.ADMIN_SECRET, data)

        headers = [
            ('Key', self.ADMIN_KEY),
            ('Sign', sign)
        ]

        rv = self.app.post(self.DELETE_URL, headers=headers, data=data)
        self.assertEqual(rv.status_code, 201)
