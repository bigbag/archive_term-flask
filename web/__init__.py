from flask import Flask, jsonify, abort, make_response

app = Flask(__name__)
app.config.from_object('configs.general.DevelopmentConfig')
# app.config.from_object('configs.general.ProductionConfig')

from flask.ext.cache import Cache

cache = Cache(app)

from flask.ext.mail import Mail

mail = Mail(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

users = {
    "john": "hello",
    "susan": "bye"
}


@auth.get_password
def get_password(username):
    if username in users:
        return users[username]
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

from web.views.api import api

#app.register_blueprint(api, url_prefix='/term/v1.0')
app.register_blueprint(api, url_prefix='')

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Fail'}), 500)
