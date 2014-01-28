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

# app.config.update(
#     CELERYBEAT_SCHEDULE={
#         'every-minute': {
#             'task': 'console.tasks.sms.send',
#             'schedule': crontab(minute='*/1'),
#             'args': ('7', 'test1'),
#         },
#     }
# )


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
