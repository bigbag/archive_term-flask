# -*- coding: utf-8 -*-
"""
   Входной скрипт

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web import app
app.config.from_object('configs.general.ProductionConfig')
app.run(host=app.config['APP_IP'], port=app.config['APP_PORT'])
