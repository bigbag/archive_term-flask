from flask import Flask, jsonify, abort, make_response

app = Flask(__name__)
app.config.from_object('api.configs.general.DevelopmentConfig')
# app.config.from_object('api.configs.general.ProductionConfig')

from flask.ext.cache import Cache

cache = Cache(app)

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

from api.views.term import term  # , mail, report

app.register_blueprint(term, url_prefix='/term/v1.0')
# app.register_blueprint(mail, url_prefix='/mail/v1.0')
# app.register_blueprint(report, url_prefix='/report/v1.0')


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Fail'}), 500)
