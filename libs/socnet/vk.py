# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Facebook

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from helpers import request_helper

from libs.socnet.socnet_base import SocnetBase
from models.soc_token import SocToken
from models.payment_loyalty_sharing import PaymentLoyaltySharing


class VkApi(SocnetBase):

    API_PATH = 'https://api.vk.com/method/'

    def subscription_control(self, condition_id):
        answer = False

        condition = PaymentLoyaltySharing.query.get(condition_id)
        if not condition:
            return False

        api_url = self.API_PATH \
            + 'groups.getById?group_id=' \
            + condition.data  \
            + '&fields=members_count'

        group = request_helper.make_request(api_url, True)

        if 'response' in group and len(group['response']) > 0 \
                and 'members_count' in group['response'][0]:
            answer = group['response'][0]['members_count']

        return answer

    def check_subscription(self, url, token_id, sharing_id):
        """подпиcка на группу"""
        answer = self.CONDITION_ERROR

        condition = PaymentLoyaltySharing.query.get(sharing_id)
        if not condition:
            return self.CONDITION_ERROR

        soc_token = SocToken.query.get(token_id)
        if not soc_token:
            return self.CONDITION_FAILED

        api_url = self.API_PATH \
            + 'users.getSubscriptions?user_id=' \
            + soc_token.soc_id

        userSubs = request_helper.make_request(api_url, True)

        if not ('response' in userSubs and 'groups' in userSubs['response']):
            return self.CONDITION_ERROR

        answer = self.CONDITION_FAILED

        if not ('items' in userSubs['response']['groups']):
            return answer

        for item in userSubs['response']['groups']['items']:
            if str(item) == str(condition.data):
                answer = self.CONDITION_PASSED

        return answer
