from flask import Flask, jsonify, abort, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from modules.term.views import term
from modules.mail.views import mail
from modules.report.views import report

app = Flask(__name__)
app.register_blueprint(term, url_prefix='/term/v1.0')
app.register_blueprint(mail, url_prefix='/mail/v1.0')
app.register_blueprint(report, url_prefix='/report/v1.0')

db = SQLAlchemy(app)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def not_found(error):
    return make_response(jsonify({'error': 'Fail'}), 500)
