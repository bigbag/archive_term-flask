from flask import Flask, g

app = Flask(__name__)
app.config.from_object('configs.general.Config')

from libs.redis_cache import SimpleRedisCache
cache = SimpleRedisCache(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from web.celery import celery

from libs.redis_sessions import RedisSessionInterface
app.session_interface = RedisSessionInterface()

from flask.ext.login import LoginManager
lm = LoginManager()
lm.init_app(app)

from web.views.api import admin, term, social
from web.views.term import general

app.register_blueprint(term.mod, url_prefix='/api/term')
app.register_blueprint(admin.mod, url_prefix='/api/admin')
app.register_blueprint(general.mod, url_prefix='/term')
app.register_blueprint(social.mod, url_prefix='/api/social')

if app.debug is not True:
    import logging
    from logging import Formatter
    from logging.handlers import RotatingFileHandler

    log_name = '%s/%s' % (app.config['LOG_PATH'], 'web_error.log')
    file_handler = RotatingFileHandler(
        log_name,
        maxBytes=1024 * 1024 * 100,
        backupCount=20)
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.WARNING)
    app.logger.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
