# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, терминалы фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from web.views.term.general import *

from web.form.term import TermAddForm
from web.form.event import TermEventAddForm

from models.term import Term
from models.report import Report
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

    return render_template(
        'term/terminal/index.html',
        term=Term(),
        term_types=Term().get_type_list(),
        term_blacklist=Term().get_blacklist_list()
    )


@mod.route('/terminal', methods=['POST'])
@login_required
@json_headers
def terminal_list():
    """Получаем список терминалов принадлежащих фирме"""

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

    events = Event().get_events()
    term_event = TermEvent()

    term_access = FirmTerm().get_access_by_firm_id(g.firm_info['id'], term_id)
    term_events = TermEvent.query.filter(TermEvent.term_id == term_id)

    return render_template(
        'term/terminal/view.html',
        term=term,
        events=events,
        term_event=term_event,
        term_events=term_events,
        term_access=term_access,
        term_types=Term().get_type_list(),
        term_blacklist=Term().get_blacklist_list(),
    )


@mod.route('/terminal/<int:term_id>/<action>', methods=['POST'])
@login_required
@json_headers
def terminal_save(term_id, action):
    """Добавляем или редактируем терминал"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())
    action_list = ('add', 'edit')

    if action not in action_list:
        abort(400)

    id = int(arg['id']) if 'id' in arg else None

    if 'hard_id' in arg and arg['hard_id']:
        term = Term().get_by_hard_id(arg['hard_id'])
    elif 'edit' in action:
        term = Term().get_by_id(id)
    else:
        term = Term()

    if term and term.id and term.id != id:
        answer['message'] = u'Терминал с таким SN уже есть в системе'
    else:
        form = TermAddForm.from_json(arg)
        if form.validate():
            form.populate_obj(term)

            result = False
            if 'add' in action:
                result = term.term_add(g.firm_info['id'])
            elif 'edit' in action:
                result = term.save()

            if result:
                answer['error'] = 'no'
                answer['message'] = u'Данные сохранены'
        else:
            answer[
                'message'] = u'Форма заполнена неверно, проверьте формат полей'

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/locking', methods=['POST'])
@login_required
@json_headers
def terminal_locking(term_id):
    """Блокировка и разблокировка терминал"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    if 'csrf_token' not in arg or arg['csrf_token'] != g.token:
        abort(403)

    if 'status' not in arg or 'id' not in arg:
        abort(400)

    term = Term.query.get(term_id)
    if not term:
        abort(404)

    if term.status == Term.STATUS_VALID:
        term.status = Term.STATUS_BANNED
    elif term.status == Term.STATUS_BANNED:
        term.status = Term.STATUS_VALID
    if term.save():
        answer['error'] = 'no'
        answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/remove', methods=['POST'])
@login_required
@json_headers
def terminal_remove(term_id):
    """Удаление терминала"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    if 'csrf_token' not in arg or arg['csrf_token'] != g.token:
        abort(403)

    term = Term().get_info_by_id(term_id)
    if not term:
        abort(404)

    report = Report.query.filter_by(term_id=term.id).first()

    if not report:
        if term.term_remove():
            answer['error'] = 'no'
            answer['message'] = u'Операция успешно выполнена'
    else:
        answer['message'] = u"""Невозможно удалить.
            По терминалу была совершена операция."""

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/event/<int:term_event_id>', methods=['GET'])
@login_required
def terminal_event_info(term_id, term_event_id):
    """Информация о событии привязаном к терминалу"""

    term = Term().get_info_by_id(term_id)
    if not term:
        abort(404)

    term_event = TermEvent.query.get(term_event_id)
    if not term_event:
        abort(404)

    if term_event.term_id != term.id:
        abort(400)

    events = Event().get_events()

    return render_template(
        'term/terminal/event_view.html',
        term=term,
        events=events,
        term_event=term_event
    )


@mod.route('/terminal/<int:term_id>/event/<int:term_event_id>', methods=['POST'])
@login_required
@json_headers
def terminal_event_save(term_id, term_event_id):
    """Сохраняем событие привязаное к терминалу"""
    answer = dict(error='yes', message='')
    arg = json.loads(request.stream.read())

    if 'csrf_token' not in arg or arg['csrf_token'] != g.token:
        abort(403)

    term = Term.query.get(term_id)
    if not term:
        abort(404)

    if term_event_id == 0:
        term_event = TermEvent()
    else:
        term_event = TermEvent.query.get(term_event_id)
        if not term_event:
            abort(404)

    form = TermEventAddForm.from_json(arg)
    if form.validate():
        form.populate_obj(term_event)

        term_event_old = TermEvent.query.filter_by(
            term_id=term.id, event_id=term_event.event_id).first()

        if term_event_old and (term_event.id != term_event_old.id):
            answer['message'] = u"""Такое событие уже есть,
                                    удалите старое или измените тип нового"""

        elif term_event.term_event_save(g.firm_info['id'], term.id):
            if term_event_id == 0:
                term_event.save()

            answer['error'] = 'no'
            answer['message'] = u'Данные сохранены'
    else:
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/event/<int:term_event_id>/delete', methods=['POST'])
@login_required
@json_headers
def terminal_event_delete(term_id, term_event_id):
    """Удаляем событие привязаное к терминалу"""
    answer = dict(error='yes', message='')

    arg = json.loads(request.stream.read())
    if 'csrf_token' not in arg or arg['csrf_token'] != g.token:
        abort(403)

    firm_term = FirmTerm().get_list_by_firm_id(g.firm_info['id'])
    if term_id not in firm_term:
        abort(403)

    term_event = TermEvent.query.filter_by(
        term_id=term_id, id=term_event_id).first()

    if not term_event:
        abort(400)

    if term_event.term_event_remove(g.firm_info['id']):
        answer['error'] = 'no'
        answer['message'] = u'Событие удалено'

    return jsonify(answer)
