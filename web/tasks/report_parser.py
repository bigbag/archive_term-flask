# -*- coding: utf-8 -*-

"""
    Задачи по формированию отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import time
from lxml import etree

from datetime import datetime, timedelta
from sqlalchemy.sql import func

from web import app
from web.celery import celery

from models.report import Report
from models.event import Event
from models.term import Term


from helpers import date_helper


class ReportParserTask (object):

    @staticmethod
    @celery.task
    def parser(file_name):

        return True
