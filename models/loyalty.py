# -*- coding: utf-8 -*-
"""
    Модель для акций

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from helpers import date_helper


class Loyalty(db.Model):

    __bind_key__ = 'payment'
    __tablename__ = 'loyalty'

    RULE_FIXED = 0
    RULE_RATE = 1

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

    id = db.Column(db.Integer, primary_key=True)
    terms_id = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey('person_event.id'))
    firm_id = db.Column(db.Integer)
    rules = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    amount = db.Column(db.String(32))
    threshold = db.Column(db.String(32))
    desc = db.Column(db.String(1024))
    creation_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    stop_date = db.Column(db.DateTime)
    sharing_type = db.Column(db.Integer)
    data = db.Column(db.String(1024))

    def __init__(self):
        self.rules = self.RULE_FIXED
        self.creation_date = date_helper.get_curent_date()

    def __repr__(self):
        return '<id %r>' % (self.id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(e)
            return False
        else:
            return True

    @staticmethod
    def get_action_link(action_id):
        link = ''
        userAction = Loyalty.query.filter_by(
            id=action_id).first()
        actionTag = "<a ng-click=\"checkLike(" + str(
            action_id) + ")\">"
        if actionTag in userAction.desc:
            link = userAction.desc[
                userAction.desc.find(actionTag) + len(actionTag):]
            if "</a>" in link:
                link = link[0:link.find("</a>")]
        return link
