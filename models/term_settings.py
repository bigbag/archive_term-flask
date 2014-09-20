# -*- coding: utf-8 -*-
"""
    Модель для настроек терминалов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web import db

from models.base_model import BaseModel


class TermSettings(db.Model, BaseModel):

    __bind_key__ = 'term'
    __tablename__ = 'term_settings'

    STATUS_ON = 1
    STATUS_OFF = 0

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    download_status = db.Column(db.Integer, index=True, nullable=False)
    download_ip = db.Column(db.String(150), nullable=False)
    download_port = db.Column(db.Integer, nullable=False)
    download_proto = db.Column(db.String(150), nullable=False)
    download_link_type = db.Column(db.Integer, nullable=False)
    upload_status = db.Column(db.Integer, index=True, nullable=False)
    upload_ip = db.Column(db.String(150), nullable=False)
    upload_port = db.Column(db.Integer, nullable=False)
    upload_proto = db.Column(db.String(150), nullable=False)
    upload_link_type = db.Column(db.Integer, nullable=False)
    logger_status = db.Column(db.Integer, index=True, nullable=False)
    logger_ip = db.Column(db.String(150), nullable=False)
    logger_port = db.Column(db.Integer, nullable=False)
    logger_proto = db.Column(db.String(150), nullable=False)
    logger_link_type = db.Column(db.Integer, nullable=False)
    update_status = db.Column(db.Integer, index=True, nullable=False)
    update_ip = db.Column(db.String(150), nullable=False)
    update_port = db.Column(db.Integer, nullable=False)
    update_proto = db.Column(db.String(150), nullable=False)
    update_link_type = db.Column(db.Integer, nullable=False)
    keyload_status = db.Column(db.Integer, index=True, nullable=False)
    keyload_ip = db.Column(db.String(150), nullable=False)
    keyload_port = db.Column(db.Integer, nullable=False)
    keyload_proto = db.Column(db.String(150), nullable=False)
    keyload_link_type = db.Column(db.Integer, nullable=False)

    def __init__(self):
        self.download_status = self.STATUS_ON
        self.download_ip = '5.9.50.180'
        self.download_port = 4000
        self.download_proto = 'https'
        self.download_link_type = 2
        self.upload_status = self.STATUS_ON
        self.upload_ip = '5.9.50.180'
        self.upload_port = 4000
        self.upload_proto = 'https'
        self.upload_link_type = 2
        self.logger_status = self.STATUS_OFF
        self.logger_ip = '5.9.50.180'
        self.logger_port = 9999
        self.logger_proto = 'https'
        self.logger_link_type = 2
        self.update_status = self.STATUS_OFF
        self.update_ip = '5.9.50.180'
        self.update_port = 9999
        self.update_proto = 'https'
        self.update_link_type = 2
        self.keyload_status = self.STATUS_OFF
        self.keyload_ip = '5.9.50.180'
        self.keyload_port = 9999
        self.keyload_proto = 'https'
        self.keyload_link_type = 2
