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
    arg = get_post_arg(request, True)

    arg['type'] = 'firm'
    arg['id'] = g.firm_info['id']
    answer = Report().get_person_report(**arg)

    return jsonify(answer)


@mod.route('/report/terminal', methods=['POST'])
@login_required
@json_headers
def report_get_terminal_report():
    arg = get_post_arg(request, True)

    arg['payment_type'] = Report.TYPE_WHITE
    answer = Report().get_firm_interval_report(
        g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/report/summ', methods=['POST'])
@login_required
@json_headers
def report_get_summ_report():
    arg = get_post_arg(request, True)

    arg['payment_type'] = Report.TYPE_PAYMENT
    answer = Report().get_firm_interval_report(
        g.firm_info['id'], **arg)

    return jsonify(answer)
