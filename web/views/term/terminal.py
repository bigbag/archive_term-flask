# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, терминалы фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web.views.term.general import *

from web.form.term import TermAddForm

from models.term import Term
from models.event import Event
from models.firm_term import FirmTerm
from models.term_event import TermEvent


@mod.route('/terminal/content/<path:action>', methods=['POST'])
@login_required
@json_headers
def terminal_dynamic_content(action):
    """Получаем блок для динамической вставки"""

    answer = dict(content='', error='yes')
    term = None
    term_types = None

    if action == 'form':
        term = Term()
        term_types = Term().get_type_list()

    patch = "term/terminal/%s.html" % action
    answer['content'] = render_template(
        patch,
        term_types=term_types,
        term=term)
    answer['error'] = 'no'

    return jsonify(answer)


@mod.route('/terminal', methods=['GET'])
@login_required
def terminal_view():
    """Отображаем страницу со списком терминалов, сам список получаем отдельным запросом"""

    return render_template('term/terminal/index.html')


@mod.route('/terminal', methods=['POST'])
@login_required
@json_headers
def terminal_list():
    """Получаем список терминалов принадлежащих фирме"""

    arg = json.loads(request.stream.read())
    answer = Term().select_term_list(
        g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/terminal/content/form', methods=['POST'])
@login_required
@json_headers
def terminal_form():
    """Получаем форму для редактирования и добавления терминала"""

    answer = dict(content='', error='yes')
    arg = json.loads(request.stream.read())

    term = Term()
    term_types = Term().get_type_list()
    print term_types
    if 'term_id' in arg and arg['term_id']:
        term = Term.query.get(int(arg['term_id']))

    answer['content'] = render_template(
        "term/terminal/form.html",
        term_types=term_types,
        term=term)
    answer['error'] = 'no'

    return jsonify(answer)


@mod.route('/terminal/add', methods=['POST'])
@login_required
@json_headers
def terminal_add():
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
                answer['message'] = u'Терминал успешно добавлен'
        else:
            answer['message'] = u"""Форма заполнена неверно,
                проверьте формат полей"""
    return jsonify(answer)


@mod.route('/terminal/<int:term_id>', methods=['POST'])
@login_required
@json_headers
def terminal_edit(term_id):
    """Редактируем терминал"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    term = Term.query.get(int(term_id))
    if not term:
        abort(404)

    form = TermAddForm.from_json(arg)
    if form.validate():
        form.populate_obj(term)

        if term.save():
            answer['error'] = 'no'
            answer['message'] = u'Данные сохранены'
    else:
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
    return jsonify(answer)


@mod.route('/terminal/locking', methods=['POST'])
@login_required
@json_headers
def terminal_locking():
    """Блокировка и разблокировка терминал"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    if 'csrf_token' not in arg or arg['csrf_token'] != g.token:
        abort(403)

    if 'status' not in arg or 'id' not in arg:
        abort(400)

    term = Term.query.get(int(arg['id']))
    if not term:
        abort(404)

    term.status = int(arg['status'])
    if term.save():
        answer['error'] = 'no'
        answer['message'] = u'Операция успешно выполнена'

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

    term_access = FirmTerm().get_access_by_firm_id(g.firm_info['id'], term_id)
    term_events = TermEvent.query.filter(TermEvent.term_id == term_id)

    return render_template(
        'term/terminal/view.html',
        term=term,
        term_events=term_events,
        term_access=term_access,
    )


@mod.route('/terminal/event/form', methods=['POST'])
@login_required
@json_headers
def terminal_event_add_form():
    """Отображаем форму добавления или изменения события на терминале"""
    answer = dict(error='yes', content='')
    arg = json.loads(request.stream.read())

    events = Event().get_events()
    term_event = TermEvent()

    answer['content'] = render_template(
        'term/terminal/event_form.html',
        events=events,
        term_event=term_event)
    answer['error'] = 'no'

    return jsonify(answer)


@mod.route('/terminal/event/save', methods=['POST'])
@login_required
@json_headers
def terminal_event_add():
    """Сохраняем событие привязаное к терминалу"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    print arg
    return jsonify(answer)
