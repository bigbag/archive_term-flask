# -*- coding: utf-8 -*-
from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for
from api import auth
from api.models.term import Term

term = Blueprint('term', __name__)


@term.route('/configs/config_<int:term>.xml', methods=['GET'])
#@auth.login_required
def get_tasks(term):
    admin = Term.query.filter_by(id=term).first()
    return str(admin.status)
