# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Foursquare

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet_api_base import SocnetApiBase
from models.soc_token import SocToken
from models.loyalty import Loyalty
from grab import Grab
import json
import urllib
import pprint


class FoursquareApi(SocnetApiBase):

    API_PATH = 'https://api.foursquare.com/v2/'

    def check_checkin(self, placeStr, token_id, loyalty_id):
        checkin = False

        history = self.get_history(token_id)
        action = Loyalty.query.get(loyalty_id)

        if history.has_key('response') and history['response'].has_key('venues') and history['response']['venues'].has_key('items') and len(history['response']['venues']['items']) > 0 and len(action.data) > 0:
            target = json.loads(action.data)
            for item in history['response']['venues']['items']:
                if item.has_key('venue') and item['venue'].has_key('location') and item['venue']['location'].has_key('lat') and item['venue']['location'].has_key('lng') and item['venue']['location']['lat'] == target['lat'] and item['venue']['location']['lng'] == target['lng']:
                    checkin = True

        return checkin

    def check_mayor(self, placeStr, token_id, loyalty_id):
        is_mayor = False

        mayorship = self.get_mayorship(token_id)
        action = Loyalty.query.get(loyalty_id)

        if mayorship.has_key('response') and mayorship['response'].has_key('mayorships') and mayorship['response']['mayorships'].has_key('items') and len(mayorship['response']['mayorships']['items']) > 0 and len(action.data) > 0:
            target = json.loads(action.data)
            for item in mayorship['response']['mayorships']['items']:
                if item.has_key('venue') and item['venue'].has_key('location') and item['venue']['location'].has_key('lat') and item['venue']['location'].has_key('lng') and item['venue']['location']['lat'] == target['lat'] and item['venue']['location']['lng'] == target['lng']:
                    is_mayor = True

        return is_mayor

    def check_badge(self, name, token_id, loyalty_id):
        has_badge = False

        badges = self.get_badges(token_id)

        if badges.has_key('response') and badges['response'].has_key('badges'):
            badges = badges['response']['badges']
            for badge in badges:
                if (name.replace('"', '') == badges[badge]['name']):
                    if len(badges[badge]['unlocks']) > 0:
                        has_badge = True

        return has_badge

    def get_badges(self, token_id):
        socToken = SocToken.query.get(token_id)
        return self.make_api_request(self.API_PATH + 'users/self/badges?oauth_token=' + socToken.user_token + '&v=20140206', True)

    def get_mayorship(self, token_id):
        socToken = SocToken.query.get(token_id)
        return self.make_api_request(self.API_PATH + 'users/self/mayorships?oauth_token=' + socToken.user_token + '&v=20140206', True)

    def get_history(self, token_id):
        socToken = SocToken.query.get(token_id)
        return self.make_api_request(self.API_PATH + 'users/self/venuehistory?oauth_token=' + socToken.user_token + '&v=20140205', True)

    def parse_place(self, placeStr):
        place = {}
        place['name'] = self.parse_get_param(placeStr, '"')
        if '"' in place['name']:
            place['address'] = place['name'][place['name'].find('"') + 1:]
            place['name'] = place['name'][0:place['name'].find('"')]

            place['address'] = self.parse_get_param(place['address'], '"')
            if '"' in place['address']:
                place['address'] = place['address'][
                    0:place['address'].find('"')]

        if place.has_key('address') and 0 == len(place['address']):
            place.pop('address')

        return place

    @staticmethod
    def make_api_request(url, parse_json):
        g = Grab()
        g.go(url)
        answer = g.response.body
        if parse_json:
            answer = json.loads(answer)

        return answer