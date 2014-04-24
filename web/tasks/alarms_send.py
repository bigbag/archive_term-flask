# -*- coding: utf-8 -*-
"""
    Задача рассылки уведомлений о сбоях в работе терминалов

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from web.celery import celery
import json
from models.alarm_stack import AlarmStack
from models.term import Term
from helpers import date_helper

from web.tasks import mail
from web.emails.term.term_alarm import TermAlarmMessage


@celery.task
def check_alarms():
    alarm_stack = AlarmStack.query.filter().all()

    for alarm in alarm_stack:
        term = Term().get_by_id(alarm.term_id)
        if not term:
            continue

        seans_alarm = 0
        if term.config_date:
            delta = date_helper.get_curent_date(
                format=False) - term.config_date

            if delta.total_seconds() > alarm.interval:
                recipients = json.loads(alarm.emails)
                termInfo = Term().get_info_by_id(alarm.term_id)
                for email in recipients:
                    mail.send.delay(
                        TermAlarmMessage,
                        to=email,
                        term=termInfo)
