# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, люди фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *

from web.form.person import PersonAddForm

from models.person import Person
from models.person_event import PersonEvent


@mod.route('/person/content/<path:action>', methods=['POST'])
@login_required
@json_headers
def get_person_content(action):
    """Получаем блок для динамической вставки"""

    answer = dict(content='', error='yes')
    patch = "term/person/%s.html" % action
    answer['content'] = render_template(patch)
    answer['error'] = 'no'

    return jsonify(answer)


@mod.route('/person/<path:action>', methods=['GET'])
@mod.route('/person', methods=['GET'])
@login_required
def person_view(action=None):
    """Отображаем страницу со списком сотрудников, сам список получаем отдельным запросом"""

    person = Person()
    return render_template(
        'term/person/index.html',
        person=person
    )


@mod.route('/person', methods=['POST'])
@login_required
@json_headers
def get_person_list():
    """Получаем список сотрудников фирмы"""

    arg = json.loads(request.stream.read())
    answer = Person().select_person_list(
        g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/person/<int:person_id>', methods=['GET'])
@login_required
def person_info(person_id):
    """Информация о сотруднике"""

    person = Person.query.get(person_id)

    if not person:
        abort(404)

    if person.firm_id != g.firm_info['id']:
        abort(403)

    person_events = PersonEvent().get_by_person_id(person.id)
    return render_template(
        'term/person/view.html',
        person=person,
        person_events=person_events
    )


def person_edit(arg, person_id):
    """Редактируем терминал"""
    answer = dict(error='yes', message='')

    person = Person.query.get(int(person_id))
    if not person:
        abort(404)

    form = PersonAddForm.from_json(arg)

    if form.validate():
        form.populate_obj(person)

        if person.save():
            answer['error'] = 'no'
            answer['message'] = u'Данные сохранены'
    else:
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
    return jsonify(answer)


@mod.route('/person/<int:person_id>/<action>', methods=['POST'])
@login_required
@json_headers
def person_save(person_id, action):
    """Добавляем или редактируем терминал"""
    arg = json.loads(request.stream.read())

    if 'add' in action:
        result = person_add(arg)
    elif 'edit' in action:
        result = person_edit(arg, person_id)
    else:
        abort(400)

    return result
