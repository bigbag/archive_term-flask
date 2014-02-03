# -*- coding: utf-8 -*-
"""
    Задачи по обслуживанию корпоративного кошелька

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app, db
from web.celery import celery

from models.person import Person
from models.payment_wallet import PaymentWallet
from models.term_corp_wallet import TermCorpWallet


@celery.task
def recovery_limit(interval):
    result = False
    corp_wallets = TermCorpWallet.query.filter(
        TermCorpWallet.interval == interval).filter(
            TermCorpWallet.balance != TermCorpWallet.limit).all(
            )

    for corp_wallet in corp_wallets:
        corp_wallet.balance = corp_wallet.limit
        if not corp_wallet.save():
            continue

        person = Person.query.get(corp_wallet.person_id)
        if not person:
            continue
        person.wallet_status = Person.STATUS_VALID
        if person.save():
            result = True
    return result
