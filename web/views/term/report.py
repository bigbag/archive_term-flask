# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, отчеты фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import json
import os

from web.views.term.general import *
from web import app
from flask import send_from_directory

from models.report import Report
from models.person import Person
from models.report_stack import ReportStack
from models.payment_account import PaymentAccount
from models.firm import Firm


@mod.route('/report/<action>', methods=['GET'])
@login_required
def report_select_action(action):
    """Статистика по корпоративным и личным расходам"""

    VALID_ACTITON = (
        'company',
        'money',
    )
    if not action in VALID_ACTITON:
        abort(404)

    template = 'term/report/%s.html' % action
    return render_template(template)


@mod.route('/report/company', methods=['POST'])
@login_required
@json_headers
def report_get_terminal_report():
    arg = get_post_arg(request, True)
    arg['firm_id'] = g.firm_info['id']

    if not 'report_type' in arg:
        abort(405)

    if arg['report_type'] == 'term':
        arg['payment_type'] = Report.TYPE_WHITE
        answer = Report().get_term_report(**arg)
    else:
        answer = Report().get_person_report(**arg)

    return jsonify(answer)


@mod.route('/report/money', methods=['POST'])
@login_required
@json_headers
def report_get_money_report():
    arg = get_post_arg(request, True)

    arg['payment_type'] = Report.TYPE_PAYMENT
    arg['firm_id'] = g.firm_info['id']

    answer = Report().get_term_report(**arg)

    return jsonify(answer)


@mod.route('/report/new', methods=['POST'])
@login_required
def report_create_new():
    """Создание нового или редактирование отчета"""

    answer = dict(error='yes', message=u'Произошла ошибка')

    arg = get_post_arg(request, True)
    if 'id' not in arg:
        abort(405)
    arg['firm_id'] = g.firm_info['id']

    report_stack = ReportStack.query.get(arg['id'])
    if not report_stack:
        report_stack = ReportStack()

    if 'details' in arg and 'person' in arg['details']:
        name = arg['details']['person']
        person = Person.get_by_name(g.firm_info['id'], name, 1)
        if not person:
            del arg['details']['person']
        else:
            arg['details']['person'] = person[0].id

    for key in arg:
        setattr(report_stack, key, arg[key])

    if report_stack.save():
        answer['error'] = 'no'
        answer['message'] = u'Отчет сохранен'

    return jsonify(answer)


@mod.route('/report/list', methods=['GET'])
@login_required
def report_list_page():
    """Страница отчетов"""

    return render_template(
        'term/report/list.html',
        report_stack=ReportStack(),
        type_list=ReportStack().get_type_list(),
        interval_list=ReportStack().get_interval_list(),
        excel_list=ReportStack().get_excel_list()
    )


@mod.route('/report/list', methods=['POST'])
@login_required
def report_list():
    """Выборка списка активных отчетов"""

    arg = json.loads(request.stream.read())
    answer = ReportStack().select_list(g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/report/<int:report_id>', methods=['GET'])
@login_required
def report_edit_page(report_id):
    """Страница просмотра и редактирования отчета"""

    report_stack = ReportStack.query.get(report_id)
    if not report_stack:
        abort(404)

    if report_stack.firm_id != g.firm_info['id']:
        abort(403)

    return render_template(
        'term/report/view.html',
        report_stack=report_stack,
        type_list=ReportStack().get_type_list(),
        interval_list=ReportStack().get_interval_list(),
        excel_list=ReportStack().get_excel_list()
    )


@mod.route('/report/<int:report_id>/remove', methods=['POST'])
@login_required
def report_remove(report_id):
    """Удаление отчета"""

    answer = dict(error='yes', message=u'Произошла ошибка', status=False)

    report_stack = ReportStack.query.get(report_id)
    if not report_stack:
        abort(404)

    report_stack.delete()
    answer['error'] = 'no'
    answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)


@mod.route('/report/account', methods=['GET'])
@login_required
def account_page():
    """Страница счетов"""

    firm = Firm.query.get(g.firm_info['id'])

    return render_template(
        'term/report/account.html',
        account_email=firm.account_email
    )


@mod.route('/report/account', methods=['POST'])
@login_required
def account_list():
    """Список счетов"""

    arg = json.loads(request.stream.read())
    answer = PaymentAccount().select_list(g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/report/account/add_email', methods=['POST'])
@login_required
def add_account_email():
    """Добавление e-mail в список рассылки счетов"""

    arg = get_post_arg(request, True)
    answer = dict(error='yes', message=u'Произошла ошибка')

    if not 'new_email' in arg:
        return jsonify(answer)

    firm = Firm.query.get(g.firm_info['id'])
    emails = []
    if firm.account_email and len(firm.account_email):
        emails = json.loads(firm.account_email)

    if not arg['new_email'] in emails:
        emails.append(arg['new_email'])
        firm.account_email = json.dumps(emails)
        firm.save()

    answer['error'] = 'no'
    answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)


@mod.route('/report/account/remove_email', methods=['POST'])
@login_required
def remove_account_email():
    """Удаление e-mail из списка рассылки счетов"""

    arg = get_post_arg(request, True)
    answer = dict(error='yes', message=u'Произошла ошибка')

    if not 'target_email' in arg:
        return jsonify(answer)

    firm = Firm.query.get(g.firm_info['id'])

    if not firm.account_email or not len(firm.account_email):
        return jsonify(answer)

    emails = json.loads(firm.account_email)
    if not arg['target_email'] in emails:
        return jsonify(answer)

    new_emails = [e for e in emails if not e == arg['target_email']]

    firm.account_email = json.dumps(new_emails)
    firm.save()

    answer['error'] = 'no'
    answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)


@mod.route('/report/account/pdf/<int:account_id>', methods=['GET'])
@login_required
def get_account_pdf(account_id):
    account = PaymentAccount.query.get(account_id)

    if not account.firm_id == g.firm_info['id']:
        abort(403)

    directory = '%s/%s' % (os.getcwd(), app.config['PDF_FOLDER'])

    return send_from_directory(directory, account.filename)


@mod.route('/report/act/pdf/<int:account_id>', methods=['GET'])
@login_required
def get_act_pdf(account_id):
    account = PaymentAccount.query.get(account_id)

    if not account.firm_id == g.firm_info['id']:
        abort(403)

    if not account.status == PaymentAccount.STATUS_PAID or not account.generated_date:
        abort(404)

    directory = '%s/%s' % (os.getcwd(), app.config['PDF_FOLDER'])

    if not os.path.exists('%s/%s' % (directory, account.get_act_filename(account.firm_id, account.generated_date))):
        if not account.generate_act():
            abort(404)

    return send_from_directory(directory, account.get_act_filename(account.firm_id, account.generated_date))
