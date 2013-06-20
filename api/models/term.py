from api import app
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)


class Term(db.Model):

    STATUS_VALID = 1
    STATUS_BANNED = -1

    TYPE_POS = 0
    TYPE_VENDING = 1

    __bind_key__ = 'term'
    __tablename__ = 'term'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    name = db.Column(db.String(300))
    status = db.Column(db.Integer, index=True)
    seans_date = db.Column(db.DateTime)
    report_date = db.Column(db.DateTime)
    upload_time = db.Column(db.Time)
    upload_period = db.Column(db.Integer)
    download_time = db.Column(db.Time)
    download_period = db.Column(db.Integer)

    def __init__(self, status, type):
        self.status = STATUS_VALID
        self.type = TYPE_POS

    def __repr__(self):
        return '<id %r>' % (self.id)
