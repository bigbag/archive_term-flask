# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, отчеты

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web.views.term.general import *

from models.report import Report


def to_json(model):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    data = {}
    data['fields'] = {}
    data['pk'] = getattr(model, 'id')

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        data['fields'][col.name] = getattr(model, col.name)

    return json.dumps([data])


@login_required
def report_person():
    """Отчеты по сотрудникам"""
    firm_info = g.firm_info

    return render_template(
        'term/report/person.html',
        firm_name=firm_info['name'],
        user_email=g.user.email)


@login_required
@json_headers
def select_person_report():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    answer = Report().select_person(
        firm_info['id'], **arg)

    return jsonify(answer)


@login_required
def report_term():
    """Отчеты по терминалам"""
    firm_info = g.firm_info

    return render_template(
        'term/report/term.html',
        firm_name=firm_info['name'],
        user_email=g.user.email)


@login_required
@json_headers
def select_term_report():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    answer = Report().select_person(
        firm_info['id'], **arg)

    return jsonify(answer)


@login_required
def report_summ():
    """Отчеты по суммам"""
    firm_info = g.firm_info

    return render_template(
        'term/report/summ.html',
        firm_name=firm_info['name'],
        user_email=g.user.email)


@login_required
@json_headers
def select_summ_report():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    answer = Report().select_summ(
        firm_info['id'], **arg)

    return jsonify(answer)
