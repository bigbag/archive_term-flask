# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, терминалы фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import json
from web.views.term.general import *

from web.form.term.term import TermAddForm, TermAlarmForm
from web.form.term.event import TermEventAddForm

from models.term import Term
from models.report import Report
from models.event import Event
from models.event_type import EventType
from models.firm import Firm
from models.firm_term import FirmTerm
from models.term_event import TermEvent
from models.alarm_stack import AlarmStack


@mod.route('/terminal', methods=['GET'])
@login_required
def terminal_view():
    """Отображаем страницу со списком терминалов, сам список получаем отдельным запросом"""

    return render_template(
        'term/terminal/index.html',
        term=Term(),
        term_types=Term().get_type_list(),
        term_factors=Term().get_factor_list(),
        term_blacklist=Term().get_blacklist_list()
    )


@mod.route('/terminal', methods=['POST'])
@login_required
@json_headers
def terminal_list():
    """Получаем список терминалов принадлежащих фирме"""

    arg = get_post_arg(request, True)
    answer = Term.select_term_list(
        g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>', methods=['GET'])
@login_required
def terminal_info(term_id):
    """Информация о терминале"""

    firm_terms = FirmTerm.get_list_by_firm_id(g.firm_info['id'])
    if not term_id in firm_terms:
        abort(403)

    term = Term.get_info_by_id(term_id)
    if not term:
        abort(404)

    term_access = term_id in FirmTerm.get_list_by_firm_id(g.firm_info['id'], False)
    term_events = TermEvent().get_by_term_id(term_id)
    alarm = AlarmStack(
        firm_id=g.firm_info['id'],
        term_id=term_id).get_term_alarm()
    print alarm

    return render_template(
        'term/terminal/view.html',
        term=term,
        events=EventType.get_dict(term.type),
        term_event=TermEvent(),
        term_events=term_events,
        term_access=term_access,
        term_types=Term().get_type_list(),
        term_factors=Term().get_factor_list(),
        term_blacklist=Term().get_blacklist_list(),
        alarm_stack=alarm
    )


@mod.route('/terminal/<int:term_id>/rent/info', methods=['POST'])
@login_required
def terminal_rent_info(term_id):
    """Информация о сдачи терминала в аренду"""

    answer = dict(error='yes', message=u'Произошла ошибка')

    term = Term.get_info_by_id(term_id)
    if not term:
        abort(404)

    firm_terms = FirmTerm.query.filter(
        FirmTerm.term_id == term.id).filter(
            FirmTerm.firm_id == g.firm_info[
                'id']).filter(
                    FirmTerm.firm_id != FirmTerm.child_firm_id).all(
    )

    rents = []
    for row in firm_terms:
        rents.append(row.to_json())

    answer['error'] = 'no'
    answer['message'] = ''
    answer['rents'] = rents
    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/rent/add', methods=['POST'])
@login_required
def terminal_rent_add(term_id):
    """Сдаём терминал в аренду"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)
    error = False

    if not Term.get_by_id(term_id):
        abort(404)

    firm_terms = FirmTerm.query.filter_by(
        term_id=term_id,
        firm_id=g.firm_info['id']).all()
    if not firm_terms:
        abort(405)

    child_firm = Firm.query.filter_by(sub_domain=arg['sub_domain']).first()
    if not child_firm:
        answer['message'] = u'Фирма с таким поддоменом не найдена'
        return jsonify(answer)

    if child_firm.id == g.firm_info['id']:
        answer['message'] = u'Вы не можете сдать терминал сами себе'
        return jsonify(answer)

    parent_firm_id = False
    for firm_term in firm_terms:
        parent_firm_id = firm_term.firm_id
        if firm_term.child_firm_id == child_firm.id:
            error = True

    if error:
        answer['message'] = u'Вы уже сдаете этот терминал данной фирме'
        return jsonify(answer)

    firm_term = FirmTerm()
    firm_term.term_id = term_id
    firm_term.firm_id = parent_firm_id
    firm_term.child_firm_id = child_firm.id

    if firm_term.save():
        answer['error'] = 'no'
        answer['message'] = u'Операция выполнена'

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/rent/remove', methods=['POST'])
@login_required
def terminal_rent_remove(term_id):
    """Удаляем аренду терминала"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)

    if 'id' not in arg:
        abort(405)

    term = Term.get_by_id(term_id)
    if not term:
        abort(404)

    firm_term = FirmTerm.query.get(int(arg['id']))
    if not firm_term:
        abort(404)

    firm_term.term_remove()
    answer['error'] = 'no'
    answer['message'] = u'Операция выполнена'
    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/<action>', methods=['POST'])
@login_required
@json_headers
def terminal_save(term_id, action):
    """Добавляем или редактируем терминал"""

    answer = dict(error='yes', message=u'Произошла ошибка', id=term_id)
    arg = get_post_arg(request, True)
    action_list = ('add', 'edit')

    if action not in action_list:
        abort(400)

    id = int(arg['id']) if 'id' in arg else None

    if 'hard_id' in arg:
        term = Term.get_by_hard_id(arg['hard_id'])
        if term and term.id and term.id != id:
            answer['message'] = u'Терминал с таким SN уже есть в системе'
            return jsonify(answer)

    term = Term.get_by_id(id)
    if not term:
        term = Term()

    form = TermAddForm.from_json(arg)
    if not form.validate():
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
        return jsonify(answer)

    form.populate_obj(term)

    result = False
    if 'add' in action:
        result = term.term_add(g.firm_info['id'])
    elif 'edit' in action:
        result = term.save()

    if result:
        answer['error'] = 'no'
        answer['message'] = u'Данные сохранены'
        answer['id'] = term.id
        return jsonify(answer)

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/locking', methods=['POST'])
@login_required
@json_headers
def terminal_locking(term_id):
    """Блокировка и разблокировка терминал"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)

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

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)

    term = Term.get_info_by_id(term_id)
    if not term:
        abort(404)

    report = Report.query.filter_by(term_id=term.id).first()

    if report:
        answer['message'] = u"""Невозможно удалить.
            По терминалу была совершена операция."""
        return jsonify(answer)

    if term.term_remove():
        answer['error'] = 'no'
        answer['message'] = u'Операция успешно выполнена'
        return jsonify(answer)

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/event/<int:term_event_id>', methods=['GET'])
@login_required
def terminal_event_info(term_id, term_event_id):
    """Информация о событии привязаном к терминалу"""

    term = Term.get_info_by_id(term_id)
    if not term:
        abort(404)

    term_event = TermEvent.query.get(term_event_id)
    if not term_event:
        abort(404)

    if term_event.term_id != term.id:
        abort(400)

    return render_template(
        'term/terminal/event_view.html',
        term=term,
        events=EventType.get_dict(term.type),
        term_event=term_event,
        factor=term_event.term.factor
    )


@mod.route('/terminal/<int:term_id>/event/<int:term_event_id>', methods=['POST'])
@login_required
@json_headers
def terminal_event_save(term_id, term_event_id):
    """Сохраняем событие привязаное к терминалу"""

    answer = dict(error='yes', message='Произошла ошибка')
    arg = get_post_arg(request, True)

    term = Term.query.get(term_id)
    if not term:
        abort(404)

    if term_event_id == 0:
        term_event = TermEvent()
    else:
        term_event = TermEvent.query.get(term_event_id)
        if not term_event:
            abort(404)

    arg['cost'] = int(float(arg['cost']) * Term.DEFAULT_FACTOR)
    form = TermEventAddForm.from_json(arg)
    if not form.validate():
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
        return jsonify(answer)

    form.populate_obj(term_event)
    term_event_old = TermEvent.query.filter_by(
        term_id=term.id, event_id=term_event.event_id).first()

    if term_event_old and (term_event.id != term_event_old.id):
        answer['message'] = u"""Такое событие уже есть,
                                удалите старое или измените тип нового"""
        return jsonify(answer)

    if term_event.save():
        answer['error'] = 'no'
        answer['message'] = u'Данные сохранены'
        return jsonify(answer)

    return jsonify(answer)


@mod.route('/terminal/<int:term_id>/event/<int:term_event_id>/delete', methods=['POST'])
@login_required
@json_headers
def terminal_event_delete(term_id, term_event_id):
    """Удаляем событие привязаное к терминалу"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)

    firm_term = FirmTerm.get_list_by_firm_id(g.firm_info['id'])
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


@mod.route('/alarm/new', methods=['POST'])
@login_required
def alarm_save():
    """Создание нового или редактирование оповещения"""

    answer = dict(error='yes', message=u'Произошла ошибка')

    arg = get_post_arg(request, True)
    arg['interval'] = int(arg['interval'][0:2]) * \
        60 * 60 + int(arg['interval'][3:5]) * 60

    if not 'term_id' in arg:
        abort(404)

    term = Term.get_by_id(arg['term_id'])
    if not term:
        abort(404)

    firm_term = FirmTerm.get_list_by_firm_id(g.firm_info['id'])
    if term.id not in firm_term:
        abort(403)

    alarm_stack = AlarmStack.query.filter_by(
        term_id=arg['term_id'], firm_id=g.firm_info['id']).first()
    if not alarm_stack:
        alarm_stack = AlarmStack()

    arg['emails'] = AlarmStack().encode_field(arg['emails'])
    form = TermAlarmForm.from_json(arg)
    if not form.validate():
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
        return jsonify(answer)

    form.populate_obj(alarm_stack)
    alarm_stack.firm_id = g.firm_info['id']
    if alarm_stack.save():
        answer['error'] = 'no'
        answer['message'] = u'Оповещение сохранено'

    return jsonify(answer)


@mod.route('/alarm/remove', methods=['POST'])
@login_required
def alarm_remove():
    """Удаление оповещения"""

    answer = dict(error='yes', message=u'Произошла ошибка')

    arg = get_post_arg(request, True)
    arg['firm_id'] = int(g.firm_info['id'])

    if not 'term_id' in arg or not Term.get_by_id(arg['term_id']):
        abort(404)

    term_access = arg['term_id'] in FirmTerm.get_list_by_firm_id(
        g.firm_info['id'], False)
    if not term_access:
        term_rent = FirmTerm.query.filter_by(
            term_id=arg['term_id'], child_firm_id=g.firm_info['id']).all()
        if not term_rent:
            abort(403)

    alarm_stack = AlarmStack.query.filter_by(
        term_id=arg['term_id'], firm_id=arg['firm_id']).first()
    if not alarm_stack:
        abort(404)

    alarm_stack.delete()
    answer['error'] = 'no'
    answer['message'] = u'Оповещение удалено'

    return jsonify(answer)
