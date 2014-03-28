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
