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
        'every-day': {
            'task': 'web.tasks.corp_wallet.recovery_limit',
            'schedule': crontab(hour=0, minute=11),
            'args': ('1',),
        },
        'every-wheek': {
            'task': 'web.tasks.corp_wallet.recovery_limit',
            'schedule': crontab(hour=0, minute=11, day_of_week=1),
            'args': ('2',),
        },
        'every-month': {
            'task': 'web.tasks.corp_wallet.recovery_limit',
            'schedule': crontab(hour=0, minute=22, day_of_month=1),
            'args': ('3',),
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

from web.tasks.soc_sharing import check_sharing
from web.tasks import *
