# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, отчеты фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import json

from web.views.term.general import *

from models.report import Report
from models.person import Person
from models.report_stack import ReportStack


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

    old_report_stack = ReportStack.query.filter_by(
        check_summ=report_stack.set_check_summ()).first()

    if old_report_stack and not report_stack.id:
        answer['message'] = u'Такой отчет уже есть в списке активных'
        return jsonify(answer)

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
    arg = get_post_arg(request, True)

    report_stack = ReportStack.query.get(report_id)
    if not report_stack:
        abort(404)

    report_stack.delete()
    answer['error'] = 'no'
    answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)
