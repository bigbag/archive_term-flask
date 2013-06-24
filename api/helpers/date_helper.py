# import pytz
import datetime
from api import app
from flask import request, url_for


def get_curent_date():
    client_time = datetime.datetime.utcnow()

    return client_time.strftime('%Y-%m-%d %H:%M:%S')
