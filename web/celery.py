# -*- coding: utf-8 -*-
"""
    Инициализируем очерель celery

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import absolute_import
from web import app
from celery import Celery
from celery.schedules import crontab

app.config.update(
    CELERY_TIMEZONE='Europe/Moscow',
    CELERYBEAT_SCHEDULE={
        # 'empty-recovery-limit-day': {
        #     'task': 'web.tasks.corp_wallet.recovery_limit',
        #     'schedule': crontab(hour=0, minute=11),
        #     'args': ('1',),
        # },
        # 'empty-recovery-limit-wheek': {
        #     'task': 'web.tasks.corp_wallet.recovery_limit',
        #     'schedule': crontab(hour=0, minute=11, day_of_week=1),
        #     'args': ('2',),
        # },
        # 'empty-recovery-limit-month': {
        #     'task': 'web.tasks.corp_wallet.recovery_limit',
        #     'schedule': crontab(hour=0, minute=22, day_of_month=1),
        #     'args': ('3',),
        # },
        # 'report-sender': {
        #     'task': 'web.tasks.report_send.report_manager',
        #     'schedule': crontab(minute='*/1'),
        #     'args': ('0',),
        # },
        # 'report-sender-day': {
        #     'task': 'web.tasks.report_send.report_manager',
        #     'schedule': crontab(hour=10, minute=11),
        #     'args': ('1',),
        # },
        # 'report-sender-wheek': {
        #     'task': 'web.tasks.report_send.report_manager',
        #     'schedule': crontab(hour=10, minute=10, day_of_week=1),
        #     'args': ('2',),
        # },
        # 'report-sender-month': {
        #     'task': 'web.tasks.report_send.report_manager',
        #     'schedule': crontab(hour=10, minute=25, day_of_month=1),
        #     'args': ('3',),
        # },
        # 'alarm-sender': {
        #     'task': 'web.tasks.alarms_send.alarm_manager',
        #     'schedule': crontab(minute='*/1'),
        #     'args': (),
        # },
        # 'soc_sharing_checker': {
        #     'task': 'web.tasks.soc_sharing.sharing_manager',
        #     'schedule': crontab(minute='*/1'),
        #     'args': (),
        # },
        # 'payment_check_linking': {
        #     'task': 'web.tasks.payment.check_linking_manager',
        #     'schedule': crontab(minute='*/1'),
        #     'args': (),
        # },
        'payment_payment_check': {
            'task': 'web.tasks.payment.payment_manager',
            'schedule': crontab(minute='*/1'),
            'args': (),
        },

    },
)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

from web.tasks import *
