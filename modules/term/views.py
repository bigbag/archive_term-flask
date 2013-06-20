# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth
from modules.term import *
from app.views import auth
from config import *


@term.route('/configs/config_<int:term>.xml', methods=['GET'])
@auth.login_required
def get_tasks(term):

    return str(term)
