# -*- coding: utf-8 -*-
"""
    Задачи по генерации блэк листа

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import db
from web.celery import celery

from helpers import date_helper
from models.term_blacklist import TermBlacklist


class BlacklistTask (object):

    @celery.task
    def generate_blacklist():
        new = TermBlacklist.generate_blacklist()
        old = TermBlacklist.get_all_black_list()

        black = new - old
        white = old - new
        all_card = black | white
        for payment_id in all_card:
            card = TermBlacklist.query.get(payment_id)
            if not card:
                card = TermBlacklist()
                card.payment_id = payment_id

            if payment_id in black:
                card.status = TermBlacklist.STATUS_BLACK
            else:
                card.status = TermBlacklist.STATUS_PAYMENT
            card.timestamp = date_helper.get_current_utc()
            db.session.add(card)
        db.session.commit()

        return True
