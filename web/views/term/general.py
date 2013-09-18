# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os
import json

from flask import Flask, Blueprint, render_template, redirect, url_for
from flask import session, request, g, abort, make_response, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required, make_secure_token
from web import app, cache, lm

from helpers import hash_helper, date_helper

from decorators.header import *

from models.term_user import TermUser
from models.term_user_firm import TermUserFirm
from models.firm import Firm

from web.views.term import firm_view, person_view, report_view, term_view

term = Blueprint('term', __name__)


@lm.user_loader
def load_user(id):
    return TermUser().get_by_id(id)


@term.before_request
def before_request():
    g.user = current_user
    g.firm_info = get_firm_name(request)


@lm.unauthorized_handler
def unauthorized():
    return login_form()


def set_json_response(data, code=200):
    return make_response(jsonify(data), code)


def get_firm_name(request):
    """Определяем название фирмы по субдомену"""

    if 'firm_info' in session:
        return session['firm_info']
    else:
        result = False
        headers = request.headers
        if 'Host' in headers:
            host = request.headers['Host']
            host_name = host.split('.')
            firm = Firm().get_by_sub_domain(host_name[0])
            if firm:
                name = firm.name
                result = dict(name=firm.name, id=firm.id)
                session['firm_info'] = result
        return result


@term.route('/login', methods=['GET'])
def login_form():
    """Форма логина"""

    firm_info = get_firm_name(request)
    if not firm_info:
        abort(403)

    return render_template(
        'term/login.html',
        firm_name=firm_info['name'])


@term.route('/login', methods=['POST'])
def login():
    """Логин"""
    answer = dict(error='yes', message='')
    user = request.get_json()

    if not 'email' in user or not 'password' in user:
        abort(400)

    firm_info = get_firm_name(request)
    if not firm_info:
        abort(403)

    term_user = TermUser().get_by_email(user['email'])

    if not term_user:
        answer['message'] = u"""У нас на сайте нет пользователя с такой парой "логин - пароль".
                            Пожалуйста, проверьте введенные данные или
                            воспользуйтесь функцией восстановления пароля."""
        return set_json_response(answer)

    if term_user.status == TermUser.STATUS_NOACTIVE:
        answer['message'] = u'Пользователь не активирован'
        return set_json_response(answer)
    elif term_user.status == TermUser.STATUS_BANNED:
        answer['message'] = u'Пользователь заблокирован'
        return set_json_response(answer)

    if not hash_helper.check_password(term_user.password, user['password']):
        answer['message'] = u'Пароль не верен'
        return set_json_response(answer)

    user_firm = TermUserFirm.query.filter_by(
        user_id=term_user.id, firm_id=firm_info['id']).first()
    if not user_firm:
        answer['message'] = u'У вас нет доступа к данной фирме'
        return set_json_response(answer)

    login_user(term_user, True)
    answer['error'] = 'no'
    return set_json_response(answer)


@term.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    del session['firm_info']
    return redirect('/')


@term.route('/forgot', methods=['GET'])
def get_forgot():
    """Страница востановления пароля"""
    return render_template(
        'term/forgot.html')

term.add_url_rule(
    '/',
    view_func=report_view.report_by_person,
    methods=['GET',
             ])
term.add_url_rule(
    '/report',
    view_func=report_view.report_by_person,
    methods=['GET', ]
)
term.add_url_rule(
    '/report/person',
    view_func=report_view.report_by_person,
    methods=['GET', ]
)

term.add_url_rule(
    '/report/person/select',
    view_func=report_view.select_person_report,
    methods=['POST', ]
)
