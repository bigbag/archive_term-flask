from flask import Flask

app = Flask(__name__)
app.config.from_object('configs.general.ProductionConfig')
# app.config.from_object('configs.general.DevelopmentConfig')

from flask.ext.cache import Cache

cache = Cache(app)

from flask.ext.mail import Mail
mail = Mail(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

if app.config['LOG_ENABLE']:
    import logging
    import logging.config

    logging.config.dictConfig(app.config['LOG_SETTINGS'])
