# -*- coding: utf-8 -*-
"""
    Настройки коммуникаций для терминала

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""


class TermConfig(object):
    NTP_SERVER = 'pool.ntp.org'

    DOWNLOAD = True
    DOWNLOAD_IP = '5.9.50.180'
    DOWNLOAD_PORT = 4000
    DOWNLOAD_PROTO = 'https'
    DOWNLOAD_LINK_TYPE = 2

    UPLOAD = True
    UPLOAD_IP = '5.9.50.180'
    UPLOAD_PORT = 4000
    UPLOAD_PROTO = 'https'
    UPLOAD_LINK_TYPE = 2

    LOGGER = True
    LOGGER_IP = '80.90.125.219'
    LOGGER_PORT = 64141
    LOGGER_PROTO = 'http'
    LOGGER_LINK_TYPE = 2

    UPDATE = True
    UPDATE_IP = '80.90.125.219'
    UPDATE_PORT = 64141
    UPDATE_PROTO = 'http'
    UPDATE_LINK_TYPE = 2
    UPDATE_PERIOD = 1440


class TermOldConfig(object):

    COMM_IP = '5.9.50.180'
    COMM_PORT = 4001
    COMM_PROTO = 'https'
    COMM_LINK_TYPE = 2

    UPLOAD = True
    UPLOAD_IP = '5.9.50.180'
    UPLOAD_PORT = 4000
    UPLOAD_PROTO = 'https'
    UPLOAD_LINK_TYPE = 2

    LOGGER = True
    LOGGER_IP = '80.90.125.219'
    LOGGER_PORT = 64141
    LOGGER_PROTO = 'https'
    LOGGER_LINK_TYPE = 2

    UPDATE = True
    UPDATE_IP = '80.90.125.219'
    UPDATE_PORT = 64141
    UPDATE_PROTO = 'https'
    UPDATE_LINK_TYPE = 2
    UPDATE_PERIOD = 1440
