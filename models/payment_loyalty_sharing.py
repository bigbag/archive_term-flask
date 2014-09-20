# -*- coding: utf-8 -*-
"""
    Модель для условий акций

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import db

from models.base_model import BaseModel


class PaymentLoyaltySharing(db.Model, BaseModel):

    __bind_key__ = 'payment'
    __tablename__ = 'loyalty_sharing'

    id = db.Column(db.Integer, primary_key=True)
    loyalty_id = db.Column(db.Integer)
    sharing_type = db.Column(db.Integer)
    desc = db.Column(db.Text())
    data = db.Column(db.Text())
    link = db.Column(db.Text())
    control_value = db.Column(db.String(256))

    @staticmethod
    def get_action_link(sharing_id):
        link = False

        sharing = PaymentLoyaltySharing.query.filter_by(
            id=sharing_id).first()
        if sharing and sharing.link:
            link = sharing.link

        return link
