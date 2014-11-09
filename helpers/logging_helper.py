# -*- coding: utf-8 -*-
"""
    Хелпер для инициализации логирования

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""


def init(app):
    if not app.config['LOG_ENABLE']:
        return False

    import logging
    import logging.config

    log_settings = app.config['LOG_SETTINGS']
    for app_name in app.config['LOG_APP']:
        log_handler = "%s_handler" % app_name
        file_name = "%s/%s.log" % (app.config['LOG_PATH'], app_name)
        handlers = app.config['LOG_DEFAULT_HANFLERS'] + [log_handler, ]

        log_settings['handlers'][log_handler] = {
            'level': app.config['LOG_LEVEL'],
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'encoding': 'utf8',
            'maxBytes': app.config['LOG_MAX_SIZE'],
            'backupCount': 20,
            'filename': file_name
        }
        log_settings['loggers'][app_name] = {
            'level': app.config['LOG_LEVEL'],
            'handlers': handlers
        }
    logging.config.dictConfig(log_settings)
