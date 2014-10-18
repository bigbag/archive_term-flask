# -*- coding: utf-8 -*-
"""
    Задача рассылки уведомлений о сбоях в работе терминалов

    :copyright: (c) 2014 by Denis Amelin, Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web.celery import celery

from models.alarm_stack import AlarmStack
from models.term import Term

from helpers import date_helper

from web.tasks import mail
from web.emails.term.term_alarm import TermAlarmMessage


@celery.task
def alarm_manager():
    alarm_stack = AlarmStack.query.filter(AlarmStack.count != 0).all()
    for alarm in alarm_stack:
        term = Term.get_by_id(alarm.term_id)
        if not term:
            continue

        if not term.config_date:
            continue

        delta = date_helper.get_curent_date(format=False) - term.config_date
        if delta.total_seconds() <= alarm.interval:
            continue

        alarm.count -= 1
        alarm.save()

        emails = alarm.decode_field(alarm.emails)
        term_info = Term.get_info_by_id(alarm.term_id)
        for email in emails:
            mail.send.delay(
                TermAlarmMessage,
                to=email,
                term=term_info)
        return True
    return False
