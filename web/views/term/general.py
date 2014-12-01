# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, отчеты фасад

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json

from flask import Blueprint, render_template, redirect
from flask import session, request, g, abort, jsonify
from flask.ext.login import (login_user, logout_user, current_user,
                             login_required)
from web import cache, lm

from helpers import hash_helper

from decorators.header import *

from models.term_user import TermUser
from models.term_user_firm import TermUserFirm
from models.firm import Firm

from web.tasks import mail
from web.emails.term.user_forgot_password import UserForgotPasswordMessage

mod = Blueprint('term', __name__)


def get_general_url():
    return '/report/company'


@lm.user_loader
def load_user(id):
    key = 'term_user_%s' % str(id)
    if not cache.get(key):
        user = TermUser().get_by_id(id)
        cache.set(key, user, 3600)
    return cache.get(key)


@mod.before_request
def before_request():
    g.user = current_user
    g.firm_info = get_firm_name(request)
    g.token = hash_helper.get_user_token(request)
    g.show_account = firm_has_account(request)


@lm.unauthorized_handler
def unauthorized():
    return login_form()


def get_post_arg(request, token=False):
    arg = json.loads(request.stream.read())
    if token:
        if 'csrf_token' not in arg or arg['csrf_token'] != g.token:
            abort(403)

    return arg


def get_firm_name(request):
    """Определяем название фирмы по субдомену"""

    if 'firm_info' in session:
        return session['firm_info']

    result = False
    headers = request.headers
    if 'Host' in headers:
        host = request.headers['Host']
        host_name = host.split('.')
        firm = Firm.get_by_sub_domain(host_name[0])

        if firm:
            result = dict(name=firm.name, id=firm.id)
            session['firm_info'] = result
    return result


def firm_has_account(request):
    """Определяем необходимость страницы Счет"""

    if 'firm_has_account' in session:
        return session['firm_has_account']

    result = False
    headers = request.headers
    if 'Host' in headers:
        host = request.headers['Host']
        host_name = host.split('.')
        firm = Firm.get_by_sub_domain(host_name[0])

        if firm:
            if firm.transaction_percent or firm.transaction_comission:
                result = True
            session['firm_has_account'] = result

    return result


def get_error(message, code):
    return render_template(
        'term/error.html',
        message=message,
        code=code), code


@mod.errorhandler(400)
def bag_request(error):
    return get_error('Bad request', 400)


@mod.errorhandler(403)
def forbidden(error):
    return get_error('Forbidden', 403)


@mod.errorhandler(404)
def not_found(error):
    return get_error('Not found', 404)


@mod.errorhandler(405)
def method_not_allowed(error):
    return get_error('Method Not Allowed', 405)


@mod.route('/', methods=['GET'])
@mod.route('/login', methods=['GET'])
def login_form():
    """Форма логина"""

    if g.user.is_authenticated():
        return redirect(get_general_url())

    firm_info = g.firm_info
    if not firm_info:
        abort(403)

    return render_template('term/login.html')


@mod.route('/login', methods=['POST'])
def login():
    """Логин"""
    answer = dict(content='', error='yes')
    arg = json.loads(request.stream.read())

    if not 'email' in arg or not 'password' in arg:
        abort(400)

    firm_info = g.firm_info
    if not firm_info:
        abort(403)

    term_user = TermUser().get_by_email(arg['email'])

    if not term_user:
        answer['content'] = u"""На сайте нет пользователя с такой парой "логин - пароль".
                            Пожалуйста, проверьте введенные данные или
                            воспользуйтесь функцией восстановления пароля."""
        return jsonify(answer)

    if term_user.status == TermUser.STATUS_NOACTIVE:
        answer['content'] = u'Пользователь не активирован'
        return jsonify(answer)

    if term_user.status == TermUser.STATUS_BANNED:
        answer['content'] = u'Пользователь заблокирован'
        return jsonify(answer)

    if not hash_helper.check_password(term_user.password, arg['password']):
        answer['content'] = u'Пароль не верен'
        return jsonify(answer)

    user_firm = TermUserFirm.query.filter_by(
        user_id=term_user.id, firm_id=firm_info['id']).first()
    if not user_firm:
        answer['content'] = u'У вас нет доступа к данной фирме'
        return jsonify(answer)

    login_user(term_user, True)
    answer['error'] = 'no'
    return jsonify(answer)


@mod.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    del session['firm_info']
    return redirect('/')


@mod.route('/forgot', methods=['GET'])
def forgot():
    """Страница запроса на восстановление пароля"""
    return render_template(
        'term/forgot.html')


@mod.route('/forgot', methods=['POST'])
def forgot_request():
    """Обработка запроса на востановление пароля"""

    answer = dict(content='', error='yes')
    arg = json.loads(request.stream.read())

    term_user = TermUser().get_by_email(arg['email'])

    if not term_user:
        answer['content'] = u"""На сайте нет пользователя с таким логином".
                            Пожалуйста, проверьте введенные данные."""
        return jsonify(answer)

    if term_user.status == TermUser.STATUS_NOACTIVE:
        answer['content'] = u'Пользователь не активирован'
        return jsonify(answer)

    if term_user.status == TermUser.STATUS_BANNED:
        answer['content'] = u'Пользователь заблокирован'
        return jsonify(answer)

    recovery_url = term_user.get_change_password_url(
        request.headers.get('Origin'))

    mail.send.delay(
        UserForgotPasswordMessage,
        to=term_user.email,
        recovery_url=recovery_url)

    answer['content'] = u"""По указанному вами адресу отправлено письмо
                        с информацией о востановлении пароля."""
    answer['error'] = 'no'

    return jsonify(answer)


@mod.route('/change/<int:user_id>/<recovery_token>', methods=['GET'])
def change(user_id, recovery_token):
    """Страница востановления пароля"""

    term_user = TermUser.query.get(user_id)

    if term_user.activkey != recovery_token:
        return redirect('/')

    return render_template(
        'term/change_password.html',
        user=term_user)


@mod.route('/change', methods=['POST'])
def change_request():
    """Запрос на смену пароля"""

    answer = dict(content='', error='yes')
    arg = get_post_arg(request, True)

    term_user = TermUser.query.get(arg['id'])

    if term_user.activkey != arg['recovery_token']:
        abort(404)

    firm_info = g.firm_info
    if not firm_info:
        abort(403)

    user_firm = TermUserFirm.query.filter_by(
        user_id=term_user.id, firm_id=firm_info['id']).first()
    if not user_firm:
        answer['content'] = u'У вас нет доступа к данной фирме'
        return jsonify(answer)

    term_user.password = hash_helper.get_password_hash(arg['password'])
    term_user.activkey = hash_helper.get_activkey(term_user.password)

    if term_user.save():
        answer[
            'content'] = u'Смена пароля завершена'
        answer['error'] = 'no'

        login_user(term_user, True)

    return jsonify(answer)


@mod.route('/report/', methods=['GET'])
@mod.route('/report', methods=['GET'])
def default():
    """Перенаправление на вид по умолчанию"""
    return redirect(get_general_url())


from web.views.term import report, terminal, person
