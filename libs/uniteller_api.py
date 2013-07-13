# -*- coding: utf-8 -*-
"""
    Библиотека для работы с сервисом Uniteller

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import string


class UnitellerApi(object):
    EMPTY_ORDER = dict(
        order_id='',
        amount='',
        mean_type='',
        money_type='',
        life_time='',
        customer_id='',
        card_id='',
        l_data='',
        paymen_type='',
    )

    def __init__(self, const):
        self.const = const
        self.shop_id = self.const.SHOP_ID
        self.password = self.const.PASSWORD
        self.login = self.const.LOGIN
        self.prefix = self.const.TEST and self.const.TEST_PREFIX or self.const.DEFAULT_PREFIX

    def __repr__(self):
        return "%s" % self.const

    def get_payment_url(self):
        return "%s%s" % (self.prefix, self.const.PAYMENT_URL)

    def get_result_url(self):
        return "%s%s" % (self.prefix, self.const.RESULT_URL)

    def get_unblock_url(self):
        return "%s%s" % (self.prefix, self.const.UNBLOCK_URL)

    def get_recurrent_url(self):
        return "%s%s" % (self.prefix, self.const.RECURRENT_URL)

    def get_sing(self, order):
        result = [hashlib.md5(str(value)).hexdigest() for value in order]

        return string.upper(hashlib.md5(str('&'.join(result))).hexdigest())

    def get_recurrent_sing(self, order):
        data = (
            self.shop_id,
            order['order_id'],
            order['amount'],
            order['parent_order_id'],
            self.password)

        return self.get_sing(data)

    def get_payment_sing(self, order):
        full_order = dict(self.EMPTY_ORDER, **order)
        data = (
            self.shop_id,
            full_order['order_id'],
            full_order['amount'],
            full_order['mean_type'],
            full_order['money_type'],
            full_order['life_time'],
            full_order['customer_id'],
            full_order['card_id'],
            full_order['l_data'],
            full_order['paymen_type'],
            self.password)

        return self.get_sing(data)





 # public function getPaySign($order)  {
 #    $keys=array(
 #      $this->shopId,
 #      (!empty($order['orderId']))?$order['orderId']:'',
 #      (!empty($order['amount']))?$order['amount']:'',
 #      (!empty($order['meanType']))?$order['meanType']:'',
 #      (!empty($order['eMoneyType']))?$order['eMoneyType']:'',
 #      (!empty($order['lifeTime']))?$order['lifeTime']:'',
 #      (!empty($order['customerId']))?$order['customerId']:'',
 #      (!empty($order['cardId']))?$order['cardId']:'',
 #      (!empty($order['lData']))?$order['lData']:'',
 #      (!empty($order['paymenType']))?$order['paymenType']:'',
 #      $this->pass,
 #    );

 #    foreach ($keys as $key => $value) {
 #      $keys[$key]=md5($value);
 #    }
