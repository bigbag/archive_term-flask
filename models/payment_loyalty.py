# -*- coding: utf-8 -*-
"""
    Модель для акций

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from helpers import date_helper

from models.base_model import BaseModel


class PaymentLoyalty(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'loyalty'

    RULE_FIXED = 0
    RULE_RATE = 1
    RULE_DISCOUNT = 2
    RULE_PRESENT = 3

    STATUS_NOT_ACTUAL = 0
    STATUS_ACTUAL = 1
    STATUS_ALL = 2
    STATUS_MY = 100

    FACEBOOK_LIKE = 1
    FACEBOOK_SHARE = 2
    TWITTER_SHARE = 3
    TWITTER_RETWIT = 4
    TWITTER_READING = 5
    TWITTER_HASHTAG = 6
    FOURSQUARE_CHECKIN = 7
    FOURSQUARE_MAYOR = 8
    FOURSQUARE_BADGE = 9
    INSTAGRAM_LIKE = 10
    INSTAGRAM_FOLLOWING = 11
    GOOGLE_CIRCLE = 12
    GOOGLE_PLUS_ONE = 13
    YOUTUBE_FOLLOWING = 14
    YOUTUBE_VIEWS = 15

    DEFAULT_COUNT = 20
    MAX_COUNT = 100

    id = db.Column(db.Integer, primary_key=True)
    terms_id = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('person_event.id'))
    firm_id = db.Column(db.Integer)
    rules = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    amount = db.Column(db.String(32))
    threshold = db.Column(db.String(32))
    desc = db.Column(db.String(1024))
    name = db.Column(db.String(128))
    creation_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    stop_date = db.Column(db.DateTime)
    sharing_type = db.Column(db.Integer)
    data = db.Column(db.String(1024))
    coupon_class = db.Column(db.String(64))
    target_url = db.Column(db.String(1024))
    limit = db.Column(db.Integer)
    timeout = db.Column(db.Integer)
    bonus_limit = db.Column(db.Integer)

    def __init__(self):
        self.rules = self.RULE_FIXED
        self.creation_date = date_helper.get_curent_date()

    def get_rules_dict(self):
        return {
            self.RULE_FIXED: 'RULE_FIXED',
            self.RULE_RATE: 'RULE_RATE',
            self.RULE_DISCOUNT: 'RULE_DISCOUNT',
            self.RULE_RATE: 'RULE_PRESENT',
        }

    def rules_const(self):
        rules_dict = PaymentLoyalty().get_rules_dict()
        rules = '-1'

        if self.rules in rules_dict:
            rules = rules_dict[self.rules]

        return rules

    @staticmethod
    def get_action_link(action_id):
        link = ''

        actionTag = "<a ng-click=\"checkLike(" + str(
            action_id) + ")\">"

        userAction = PaymentLoyalty.query.filter_by(
            id=action_id).first()
        if userAction and actionTag in userAction.desc:
            link = userAction.desc[
                userAction.desc.find(actionTag) + len(actionTag):]
            if "</a>" in link:
                link = link[0:link.find("</a>")]
        return link
