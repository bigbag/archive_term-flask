# -*- coding: utf-8 -*-
"""
    Библиотека для работы с Facebook

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from libs.socnet_api_base import SocnetApiBase
from grab import Grab
import json
from libs.facebook_api import FacebookApi


class MockFacebookApi(FacebookApi):

    TEST_PAGE = """{
   "about": "Founded June 16, 1903 by Henry Ford.",
   "can_post": true,
   "category": "Company",
   "category_list": [
      {
         "id": "152142351517013",
         "name": "Corporate Office"
      },
      {
         "id": "131962450204676",
         "name": "Car Dealership"
      }
   ],
   "checkins": 644,
   "company_overview": "Ford Motor Company",
   "founded": "June 16, 1903 by Henry Ford",
   "is_published": true,
   "location": {
      "street": "One American Road",
      "city": "Dearborn",
      "state": "MI",
      "country": "United States",
      "zip": "48126 ",
      "latitude": 42.314740802122,
      "longitude": -83.210124997692
   },
   "products": "please visit http://www.ford.com",
   "talking_about_count": 32221,
   "username": "ford",
   "website": "http://www.ford.com http://www.thefordstory.com",
   "were_here_count": 18644,
   "id": "22166130048",
   "name": "Ford Motor Company",
   "link": "https://www.facebook.com/ford",
   "likes": 2087365,
   "cover": {
      "cover_id": "10152142499900049",
      "source": "https://fbcdn-sphotos-f-a.akamaihd.net/hphotos-ak-ash4/t1/s720x720/1525728_10152142499900049_1242015424_n.jpg",
      "offset_y": 0,
      "offset_x": 0
   }
}
        """

    DATA_LIKED = """{
   "data": [
      {
         "category": "Company",
         "category_list": [
            {
               "id": "152142351517013",
               "name": "Corporate Office"
            },
            {
               "id": "131962450204676",
               "name": "Car Dealership"
            }
         ],
         "name": "Ford Motor Company",
         "created_time": "2013-12-11T08:50:48+0000",
         "id": "22166130048"
      }
   ],
   "paging": {
      "next": ""
   }
}
        """

    DATA_NOT_LIKED = """{

}
        """

    def get_page(self, url, token_id, parse_json):
        answer = self.TEST_PAGE
        if parse_json:
            answer = json.loads(answer)

        return answer

    def get_like(self, page_id, token_id, parse_json):
        answer = MockFacebookApi.DATA_NOT_LIKED
        if token_id == SocnetApiBase.TOKEN_FOR_SHARED:
            answer = MockFacebookApi.DATA_LIKED
        if parse_json:
            answer = json.loads(answer)

        return answer
