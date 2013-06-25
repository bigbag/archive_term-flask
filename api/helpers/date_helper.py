import pytz
import datetime
from datetime import datetime
from pytz import timezone
from api import app
from flask import request, url_for


def get_curent_date():
    client_time = datetime.datetime.utcnow()

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
    d_tz = utc.normalize(date)
    localetime = d_tz.astimezone(tz)
    return localetime


def convert_date_to_utc(date, input, output):
    conv = datetime.strptime(date, input)
    return to_utc(conv, app.config['TZ']).strftime(output)
