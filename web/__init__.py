from flask import Flask

app = Flask(__name__)
app.config.from_object('configs.general.Config')

from flask.ext.cache import Cache
cache = Cache(app)

from flask.ext.mail import Mail
mail = Mail(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from libs.redis_sessions import RedisSessionInterface
app.session_interface = RedisSessionInterface()

from flask.ext.login import LoginManager
lm = LoginManager()
lm.init_app(app)

from web.views.api import *
from web.views.term import *

app.register_blueprint(api_term, url_prefix='/api/term')
app.register_blueprint(api_admin, url_prefix='/api/admin')
app.register_blueprint(term, url_prefix='/term')

if app.debug is not True:
    import logging
    from logging import Formatter
    from logging.handlers import RotatingFileHandler

    log_name = '%s/%s' % (app.config['LOG_FOLDER'], 'web_error.log')
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
