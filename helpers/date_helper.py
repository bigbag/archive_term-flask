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


def get_locale_months():
    return [u'январь', u'февраль', u'март',
            u'апрель', u'май', u'июнь',
            u'июль', u'август', u'сентябрь',
            u'октябрь', u'ноябрь', u'декабрь']

            
def get_locale_months_in_genitive():
    return [u'января', u'февраля', u'марта',
            u'апреля', u'мая', u'июня',
            u'июля', u'августа', u'сентября',
            u'октября', u'ноября', u'декабря']
            

def get_current_date(format='%Y-%m-%d %H:%M:%S'):
    client_time = datetime.utcnow()
    if format:
        client_time = client_time.strftime(format)
    return client_time


def get_delta_date(delta_sec, format='%Y-%m-%d %H:%M:%S'):
    date_delta = datetime.utcnow() + timedelta(seconds=delta_sec)
    if format:
        date_delta = date_delta.strftime(format)
    return date_delta


def get_current_utc():
    return calendar.timegm(datetime.utcnow().utctimetuple())


def to_utc(date, tz):
    tz = timezone(tz)
    utc = pytz.timezone('UTC')
    d_tz = tz.normalize(tz.localize(date))
    d_utc = d_tz.astimezone(utc).replace(tzinfo=None)
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


def get_date_interval(search_date, period='day', tz=app.config['TZ']):
    search_date = search_date.date()

    start = datetime(search_date.year,
                     search_date.month,
                     search_date.day, 0, 0, 0)
    stop = datetime(search_date.year,
                    search_date.month,
                    search_date.day, 23, 59, 59)
    if period == 'week':
        day_of_week = search_date.weekday()
        start_delta = timedelta(days=day_of_week)
        start_date = search_date - start_delta
        stop_delta = timedelta(days=6 - day_of_week)
        stop_date = search_date + stop_delta

        start = datetime(start_date.year,
                         start_date.month,
                         start_date.day, 0, 0, 0)
        stop = datetime(stop_date.year,
                        stop_date.month,
                        stop_date.day, 23, 59, 59)
    elif period == 'month':
        last_day = calendar.monthrange(search_date.year, search_date.month)[1]
        start = datetime(search_date.year,
                         search_date.month,
                         1, 0, 0, 0)
        stop = datetime(search_date.year, search_date.month,
                        last_day, 23, 59, 59)

    return (to_utc(start, tz).replace(tzinfo=None),
            to_utc(stop, tz).replace(tzinfo=None))


def validate_date(d, format):
    try:
        time.strptime(d, format)
        return True
    except ValueError:
        return False


def check_for_intersection(begin1, end1, begin2, end2):
    # Input format time string "hh:mm"

    if ''.join(begin2.split(':')) > ''.join(end1.split(':')):
        return False
    elif ''.join(begin1.split(':')) > ''.join(end2.split(':')):
        return False

    return True
