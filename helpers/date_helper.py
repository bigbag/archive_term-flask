# -*- coding: utf-8 -*-
"""
    Хелпер для работы с датами

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import pytz
from datetime import datetime, timedelta
from pytz import timezone
from web import app
from flask import request, url_for


def get_curent_date():
    client_time = datetime.utcnow()

    return client_time.strftime('%Y-%m-%d %H:%M:%S')


def to_utc(date, tz):
    tz = timezone(tz)
    utc = pytz.timezone('UTC')
    d_tz = tz.normalize(tz.localize(date))
    d_utc = d_tz.astimezone(utc)
    return d_utc


def from_utc(date, tz):
    tz = timezone(tz)
    utc = pytz.timezone('UTC')
    d_tz = utc.normalize(utc.localize(date))
    localetime = d_tz.astimezone(tz)
    return localetime


def convert_date_to_utc(date, tz, input, output):
    conv = datetime.strptime(date, input)
    return to_utc(conv, tz).strftime(output)


def convert_date_from_utc(date, tz, input, output):
    conv = datetime.strptime(date, input)
    return from_utc(conv, tz).strftime(output)


def get_timezone(tzname):
    now = datetime.utcnow()
    tz = pytz.timezone(tzname)
    utc = pytz.timezone('UTC')
    utc.localize(datetime.now())

    if utc.localize(now) > tz.localize(now):
        delta = str(utc.localize(now) - tz.localize(now))
        sign = '-'
    else:
        delta = str(tz.localize(now) - utc.localize(now))
        sign = '+'

    if len(delta) < 8:
        delta = "0%s" % delta
    return "%s%s%s" % (tz.tzname(now, is_dst=False), sign, delta)


def get_week_interval(day, format=False):

    day = datetime.strptime(day, '%x')
    day_of_week = day.weekday()
    start_delta = timedelta(days=day_of_week)
    start = day - start_delta
    stop_delta = timedelta(days=6 - day_of_week)
    stop = day + stop_delta

    result = (start, stop)
    if format:
        result = '%s - %s' % (start.strftime(format), stop.strftime(format))

    return result
