import pytz
import datetime
from api import app
from flask import request, url_for


def get_curent_date():
    tz = pytz.timezone(app.config['TZ'])
    client_time = datetime.datetime.now(tz)

    return client_time.strftime('%Y-%m-%d %H:%M:%S')
