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
from models.term_event import TermEvent
from models.spot import Spot
from models.payment_wallet import PaymentWallet


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

    template_patch = 'term/person/view.html'
    if not person.hard_id:
        template_patch = 'term/person/view_empty.html'

    return render_template(
        template_patch,
        person=person,
        person_events=PersonEvent().get_by_person_id(person.id),
        term_events=TermEvent().get_by_firm_id(g.firm_info['id']),
        person_event=PersonEvent()
    )


@mod.route('/person/<int:person_id>/<action>', methods=['POST'])
@login_required
@json_headers
def person_save(person_id, action):
    """Добавляем или редактируем терминал, привязываем карту"""
    arg = json.loads(request.stream.read())

    if 'add_card' in action:
        result = person_add_card(arg, person_id)
    elif 'add' in action:
        result = person_add(arg)
    elif 'edit' in action:
        result = person_edit(arg, person_id)
    else:
        abort(400)

    return result

def person_add(arg):
    """Добавляем человека"""
    answer = dict(error='yes', message='')

    code = arg['card_code'] if 'card_code' in arg else False

    person = Person()
    form = PersonAddForm.from_json(arg)

    if code:
        linking_card = person_linking_card(code)
        if not linking_card['wallet']:
            answer['message'] = person_failed_linking_card(code)
            return jsonify(answer)
        else:
            wallet = linking_card['wallet']
            person.payment_id = wallet.payment_id
            person.hard_id = wallet.hard_id
    
    if form.validate():
        form.populate_obj(person)
        
        if person.save():
            answer['error'] = 'no'
            answer['message'] = u'Данные сохранены'
        else:
            answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
    return jsonify(answer)


def person_edit(arg, person_id):
    """Редактируем человека"""
    answer = dict(error='yes', message='')

    person = Person.query.get(person_id)
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


def person_linking_card(code):
    answer = dict(error='yes', message='', wallet=False)

    spot = Spot().get_valid_by_code(code)
    if not spot:
        answer['message'] = u'Код неверен или уже активирован'
    else:
        wallet = PaymentWallet.query.filter_by(
            discodes_id=spot.discodes_id).first()

        if not wallet:
            answer['message'] = u'Привязываемая карта отсутсвует'
        else:
            answer['wallet'] = wallet

    return answer


def person_add_card(arg, person_id):
    """Привязываем к человеку карту"""
    answer = dict(error='yes', message='')

    code = arg['card_code'] if 'card_code' in arg else False
    if not code:
        abort(400)

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    linking_card = person_linking_card(code)
    if not linking_card['wallet']:
        answer['message'] = person_failed_linking_card(code)
    else:
        wallet = linking_card['wallet']
        person.payment_id = wallet.payment_id
        person.hard_id = wallet.hard_id
        if person.save():
            answer['error'] = 'no'
            answer['message'] = u'Карта успешно привязана'

    return jsonify(answer)
