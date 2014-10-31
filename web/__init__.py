from flask import Flask, g

app = Flask(__name__)
app.config.from_object('configs.general.Config')

from libs.redis_cache import SimpleRedisCache
cache = SimpleRedisCache(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from web.celery import celery

from libs.redis_sessions import RedisSessionInterface
app.session_interface = RedisSessionInterface(app)

from flask.ext.login import LoginManager
lm = LoginManager()
lm.init_app(app)

from web.views.api import admin, term, social, internal
from web.views.term import general

app.register_blueprint(term.mod, url_prefix='/api/term')
app.register_blueprint(admin.mod, url_prefix='/api/admin')
app.register_blueprint(social.mod, url_prefix='/api/social')
app.register_blueprint(internal.mod, url_prefix='/api/internal')
app.register_blueprint(general.mod, url_prefix='/term')

if app.config['LOG_ENABLE']:
    import logging
    import logging.config

    for app_name in app.config['LOG_APP']:
        log_settings = app.config['LOG_SETTINGS'].copy()
        log_name = "log_%s" % app_name
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

        setattr(app, log_name, logging.getLogger(app_name))
