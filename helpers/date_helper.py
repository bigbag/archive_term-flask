# -*- coding: utf-8 -*-
"""
    Хелпер для работы с датами

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import pytz
import time
import calendar
from datetime import datetime, timedelta
from pytz import timezone
from web import app
from flask import request, url_for


def get_curent_date(format='%Y-%m-%d %H:%M:%S'):
    client_time = datetime.utcnow()
    if format:
        client_time = client_time.strftime(format)
    return client_time


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


def get_date_interval(search_date, period='day'):

    search_date = search_date.date()
    start = search_date
    stop = search_date + timedelta(days=1)

    if period == 'week':
        day_of_week = search_date.weekday()
        start_delta = timedelta(days=day_of_week)
        start = search_date - start_delta
        stop_delta = timedelta(days=7 - day_of_week)
        stop = search_date + stop_delta
    elif period == 'month':
        start = datetime(search_date.year, search_date.month, 1)
        stop = datetime(
            search_date.year,
            search_date.month,
            calendar.mdays[search_date.month])

    return (start, stop)


def validate_date(d, format):
    try:
        time.strptime(d, format)
        return True
    except ValueError:
        return False
