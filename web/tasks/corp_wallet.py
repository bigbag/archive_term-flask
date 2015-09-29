# -*- coding: utf-8 -*-
"""
    Задачи по обслуживанию корпоративного кошелька

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import logging

from web.celery import celery

from models.person import Person
from models.term_corp_wallet import TermCorpWallet


@celery.task
def recovery_limit(interval):
    log = logging.getLogger('task')

    result = False
    corp_wallets = TermCorpWallet.query.filter(
        TermCorpWallet.interval == interval).filter(
            TermCorpWallet.balance != TermCorpWallet.limit).all()

    for corp_wallet in corp_wallets:
        corp_wallet.balance = corp_wallet.limit
        if not corp_wallet.save():
            log.error('Fail with save corp wallet')
            continue

        person = Person.query.get(corp_wallet.person_id)
        if not person:
            message = 'Not found person_id=%s' % corp_wallet.person_id
            log.error(message)
            continue

        if person.manually_blocked == Person.STATUS_VALID:
            person.wallet_status = Person.STATUS_VALID
        if person.save():
            result = True
    return result
