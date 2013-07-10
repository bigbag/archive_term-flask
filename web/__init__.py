from flask import Flask

app = Flask(__name__)
app.config.from_object('configs.general.DevelopmentConfig')
#app.config.from_object('configs.general.ProductionConfig')

from flask.ext.cache import Cache

cache = Cache(app)

from flask.ext.mail import Mail

mail = Mail(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from web.views.api import api

app.register_blueprint(api, url_prefix='/term/v1.0')

if app.debug is not True:
    import logging
    from logging import Formatter
    from logging.handlers import RotatingFileHandler

    log_name = '%s/%s' % (app.config['LOG_FOLDER'], 'error.log')
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
