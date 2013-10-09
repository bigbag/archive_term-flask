# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, терминалы фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web.views.term.general import *

from web.form.term import TermAddForm

from models.term import Term
from models.firm_term import FirmTerm
from models.term_event import TermEvent


@mod.route('/terminal', methods=['GET'])
@login_required
def terminal_view():
    """Таблица имеющихся у фирмы терминалов"""

    term = Term()
    term_types = Term().get_type_list()

    return render_template(
        'term/terminal/view.html',
        term_types=term_types,
        term=term,
    )


@mod.route('/terminal', methods=['POST'])
@login_required
@json_headers
def get_term_list():
    """Получаем список терминалов"""
    arg = json.loads(request.stream.read())
    answer = Term().select_term_list(
        g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>', methods=['GET'])
@login_required
def terminal_info(term_id):
    """Информация о терминале"""
    if not term_id in FirmTerm().get_list_by_firm_id(g.firm_info['id']):
        abort(403)

    term = Term().get_info_by_id(term_id)
    if not term:
        abort(404)

    term_types = Term().get_type_list()
    term_events = TermEvent.query.filter(TermEvent.term_id == term_id)

    return render_template(
        'term/terminal/info.html',
        term=term,
        term_events=term_events,
        term_types=term_types
    )


@mod.route('/terminal/<int:term_id>', methods=['POST'])
@login_required
@json_headers
def edit_term(term_id):
    """Редактируем терминал"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    term = Term.query.get(int(arg['id']))
    if not term:
        abort(404)

    form = TermAddForm.from_json(arg)
    if form.validate():
        form.populate_obj(term)

        if term.save():
            answer['error'] = 'no'
            answer['message'] = u'Данные сохранены'
    else:
        answer[
            'message'] = u'Форма заполнена неверно, проверьте формат полей'
    return jsonify(answer)


@mod.route('/terminal/add', methods=['POST'])
@login_required
@json_headers
def add_term():
    """Добавляем терминал"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    term = Term.query.get(int(arg['id']))

    if term:
        answer['message'] = u'Терминал с таким ID уже есть в системе'
    else:
        form = TermAddForm.from_json(arg)
        if form.validate():
            term = Term()
            form.populate_obj(term)

            if term.save():
                firm_term = FirmTerm()
                firm_term.term_id = term.id
                firm_term.firm_id = g.firm_info['id']
                firm_term.child_firm_id = firm_term.firm_id
                firm_term.save()

                answer['error'] = 'no'
                answer['message'] = u"""Терминал успешно добавлен,
                    в течении двух минут он отобразится в списке ваших терминалов"""
        else:
            answer[
                'message'] = u'Форма заполнена неверно, проверьте формат полей'
    return jsonify(answer)
