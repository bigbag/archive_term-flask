from flask import Flask, jsonify, abort, make_response

app = Flask(__name__)
# app.config.from_object('configs.general.DevelopmentConfig')
app.config.from_object('configs.general.ProductionConfig')

from flask.ext.mail import Mail

mail = Mail(app)

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
