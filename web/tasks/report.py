# -*- coding: utf-8 -*-
"""
    Задачи по формированию отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app
from web.celery import celery

from models.report import Report
from models.report_stack import ReportStask


@celery.task
def report_generate(interval):
    return True
