# -*- coding: utf-8 -*-
"""
    Контролер реализующий веб интерфейс терминального проекта

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import re
import os

from flask import Flask, Blueprint, render_template, redirect, url_for
from flask import request, g, abort, make_response, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from web import app, cache, lm

from helpers import hash_helper

from models.term_user import TermUser

term = Blueprint('term', __name__)


@lm.user_loader
def load_user(id):
    return TermUser.query.get(int(id))


@term.before_request
def before_request():
    g.user = current_user


@lm.unauthorized_handler
def unauthorized():
    return login_form()


def get_json_response(data, code=200):
    return make_response(jsonify(data), code)


@term.route('/login', methods=['GET'])
def login_form():
    """Форма логина"""
    return render_template(
        'term/login.html')


@term.route('/login', methods=['POST'])
def login():
    """Логин"""
    user = request.get_json(True)

    if not 'email' in user or not 'password' in user:
        abort(400)

    term_user = TermUser().get_by_email(user['email'])

    if not term_user:
        abort(403)

    if not hash_helper.check_password(term_user.password, user['password']):
        abort(403)

    login_user(term_user, True)

    return 'True'


@term.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('.login'))


@term.route('/', methods=['GET'])
@login_required
def get_index():
    """Главная страница"""
    return render_template(
        'term/general.html')


@term.route('/forgot', methods=['GET'])
def get_forgot():
    """Страница востановления пароля"""
    return render_template(
        'term/forgot.html')
