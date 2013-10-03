# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, отчеты фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *
from models.report import Report


@mod.route('/report/<action>', methods=['GET'])
@login_required
def report_report_action(action):
    """Отчеты по сотрудникам, терминалам, оборотам"""

    VALID_ACTITON = (
        'person',
        'terminal',
        'summ',
    )
    if not action in VALID_ACTITON:
        abort(404)

    template = 'term/report/%s.html' % action
    return render_template(template)


@mod.route('/report/person', methods=['POST'])
@login_required
@json_headers
def report_get_person_report():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())

    answer = Report().select_person(
        firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/report/terminal', methods=['POST'])
@login_required
@json_headers
def report_get_terminal_report():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    arg['payment_type'] = Report.TYPE_WHITE
    answer = Report().get_interval_report(
        firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/report/summ', methods=['POST'])
@login_required
@json_headers
def report_get_summ_report():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    arg['payment_type'] = Report.TYPE_PAYMENT
    answer = Report().get_interval_report(
        firm_info['id'], **arg)

    return jsonify(answer)
