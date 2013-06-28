# -*- coding: utf-8 -*-
"""
    Контролер реализующий апи для почтовых сообщений

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask, jsonify, abort, request, make_response, url_for
from modules.mail import *
from app.views import auth
