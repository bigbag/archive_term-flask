from flask import Flask

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

from helpers import logging_helper
logging_helper.init(app)
