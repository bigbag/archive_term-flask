# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, люди фасад

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
from datetime import datetime

from web import db
from web.views.term.general import *

from web.form.term.person import PersonAddForm
from web.form.term.event import PersonEventAddForm

from models.person import Person
from models.report import Report
from models.person_event import PersonEvent
from models.term_event import TermEvent
from models.spot import Spot
from models.payment_wallet import PaymentWallet
from models.term_corp_wallet import TermCorpWallet

from helpers import request_helper


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


@mod.route('/person/content/<path:action>', methods=['POST'])
@mod.route('/person', methods=['POST'])
@login_required
@json_headers
def get_person_list():
    """Получаем список сотрудников фирмы"""

    arg = json.loads(request.stream.read())
    answer = Person.select_list(g.firm_info['id'], **arg)

    return jsonify(answer)


@mod.route('/person/search', methods=['POST'])
@login_required
@json_headers
def get_person_search_result():
    """Поиск сотрудников по запросу"""

    answer = dict(error='yes', result={})
    arg = json.loads(request.stream.read())
    if 'request' not in arg:
        abort(400)

    limit = arg['limit'] if 'limit' in arg else 5
    result = Person.get_by_name(g.firm_info['id'], arg['request'], limit)

    answer['error'] = 'no'
    answer['result'] = [row.name for row in result]

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

    term_events = TermEvent().get_by_firm_id(g.firm_info['id'])
    term_event = TermEvent()
    if term_events:
        term_event.id = term_events[0].id

    corp_wallet = TermCorpWallet.query.filter_by(
        person_id=person.id).first()
    if not corp_wallet:
        corp_wallet = TermCorpWallet()

    return render_template(
        'term/person/view.html',
        person=person,
        person_event=PersonEvent(),
        person_events=PersonEvent.get_by_person_id(person.id),
        term_event=term_event,
        term_events=term_events,
        corp_wallet=corp_wallet,
        corp_wallet_interval=TermCorpWallet().get_interval_list()
    )


@mod.route('/person/<int:person_id>/add', methods=['POST'])
@mod.route('/person/<int:person_id>/edit', methods=['POST'])
@login_required
@json_headers
def person_save(person_id):
    """Добавляем или редактируем человека"""

    answer = dict(error='yes', message=u'Произошла ошибка', person_id=0)
    arg = json.loads(request.stream.read())
    form = PersonAddForm.from_json(arg)

    if person_id == 0:
        code = arg['card_code'] if 'card_code' in arg else False
        person = Person()

        if code:
            bind_card = set_person_card(code)
            if not bind_card['wallet']:
                answer['message'] = bind_card['message']
                return jsonify(answer)
            else:
                wallet = bind_card['wallet']
                person.payment_id = wallet.payment_id
                person.hard_id = wallet.hard_id
    else:
        person = Person.query.get(person_id)
        if not person:
            abort(404)

    if not form.validate():
        answer['message'] = u"""Форма заполнена неверно,
                            проверьте формат полей"""
        return jsonify(answer)

    form.populate_obj(person)
    if person.save():
        answer['person_id'] = person.id
        answer['error'] = 'no'
        answer['message'] = u'Данные сохранены'
        return jsonify(answer)

    return jsonify(answer)


@mod.route('/person/parsexls', methods=['POST'])
@login_required
@json_headers
def person_parse_xls():
    """Получение списка сотрудников из *.xls для импорта"""
    answer = dict(
        error='yes',
        message=u'Неверный формат файла',
        employers=[]
    )

    filepath = Person.save_import_file(request)
    if not filepath:
        abort(405)

    answer['employers'] = Person.excel_to_json_import(filepath)

    if(os.path.exists(filepath)):
        os.remove(filepath)

    if len(answer['employers']) > 0:
        answer['error'] = 'no'
        answer['message'] = 'Файл успешно загружен'

    return jsonify(answer)


@mod.route('/person/import', methods=['POST'])
@login_required
@json_headers
def person_import():
    """Импорт списка сотрудников из json"""
    answer = dict(
        error='yes',
        wrong_forms=[],
        wrong_cards=[],
        added_forms=0
    )

    data = json.loads(request.stream.read())
    employers = data['employers']
    for json_employer in employers:

        if not len(json_employer['name']):
            answer['wrong_forms'].append(json_employer)
            continue

        employer = request_helper.name_together(json_employer)
        if employer['birthday'] and len(employer['birthday']):
            try:
                employer['birthday'] = datetime.strptime(
                    employer['birthday'], '%d.%m.%Y')
                employer['birthday'] = employer[
                    'birthday'].strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                answer['wrong_forms'].append(json_employer)
                continue

        if not len(employer['tabel_id']):
            employer['tabel_id'] = None

        employer['firm_id'] = g.firm_info['id']
        employer['csrf_token'] = data['csrf_token']
        person = Person()

        form = PersonAddForm.from_json(employer)
        if not form.validate():
            answer['wrong_forms'].append(json_employer)
            continue

        form.populate_obj(person)
        code = employer['code'] if 'code' in employer else False
        if code and len(code) == 10:
            bind_card = set_person_card(code)
            if bind_card['wallet']:
                wallet = bind_card['wallet']
                person.payment_id = wallet.payment_id
                person.hard_id = wallet.hard_id
            else:
                answer['wrong_cards'].append(json_employer)
        else:
            answer['wrong_cards'].append(json_employer)

        answer['added_forms'] = answer['added_forms'] + 1
        db.session.add(person)

    if db.session.commit():
        answer['error'] = 'no'

    return jsonify(answer)


@mod.route('/person/<int:person_id>/bind_card', methods=['POST'])
@login_required
@json_headers
def person_bind_card(person_id):
    """Привязываем к человеку карту"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = json.loads(request.stream.read())

    code = arg['card_code'] if 'card_code' in arg else False
    if not code:
        abort(400)

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    bind_card = set_person_card(code)
    if not bind_card['wallet']:
        answer['message'] = bind_card['message']
        return jsonify(answer)

    wallet = bind_card['wallet']
    person.payment_id = wallet.payment_id
    person.hard_id = wallet.hard_id
    person.status = Person.STATUS_VALID
    if person.save():
        answer['error'] = 'no'
        answer['message'] = u'Карта успешно привязана'

    return jsonify(answer)


def set_person_card(code):
    answer = dict(error='yes', message=u'Произошла ошибка', wallet=False)

    spot = Spot().get_valid_by_code(code)
    if not spot:
        answer['message'] = u'Код активации не верен'
        return answer

    wallet = PaymentWallet.query.filter_by(
        discodes_id=spot.discodes_id).first()

    if not wallet:
        answer['message'] = u'Привязываемая карта отсутсвует'
        return answer

    person = Person.query.filter_by(
        payment_id=wallet.payment_id).first()

    if person:
        answer['message'] = u'Данная карта уже привязана'
        return answer

    answer['wallet'] = wallet
    return answer


@mod.route('/person/<int:person_id>/unbind_card', methods=['POST'])
@login_required
@json_headers
def person_unbind_card(person_id):
    """Отвязываем карту от человека"""

    answer = dict(error='yes', message=u'Произошла ошибка')

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    person.payment_id = None
    person.hard_id = None
    person.status = Person.STATUS_BANNED
    if person.save():
        answer['error'] = 'no'
        answer['message'] = u'Карта успешно отвязана'

    return jsonify(answer)


@mod.route('/person/<int:person_id>/lock', methods=['POST'])
@login_required
def person_lock(person_id):
    """Блокировка сотрудника"""

    answer = dict(error='yes', message='Произошла ошибка', status=False)
    arg = get_post_arg(request, True)

    if 'status' not in arg or 'id' not in arg:
        abort(400)

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    corp_wallet = TermCorpWallet.query.filter_by(person_id=person.id).first()
    if corp_wallet:
        if person.status == Person.STATUS_VALID:
            corp_wallet.status = TermCorpWallet.STATUS_BANNED
        elif person.status == Person.STATUS_BANNED:
            corp_wallet.status = TermCorpWallet.STATUS_ACTIVE

    if person.status == Person.STATUS_VALID:
        person.status = Person.STATUS_BANNED
        PersonEvent.set_status_by_person_id(
            person_id, PersonEvent.STATUS_BANNED)

    elif person.status == Person.STATUS_BANNED:
        person.status = Person.STATUS_VALID
        PersonEvent.set_status_by_person_id(
            person_id, PersonEvent.STATUS_ACTIVE)

    if person.save():
        if corp_wallet:
            corp_wallet.save()
        answer['error'] = 'no'
        answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)


@mod.route('/person/<int:person_id>/remove', methods=['POST'])
@login_required
def person_remove(person_id):
    """Удаление сотрудника"""

    answer = dict(error='yes', message=u'Произошла ошибка', status=False)

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    person.person_remove()
    answer['error'] = 'no'
    answer['message'] = u'Операция успешно выполнена'

    return jsonify(answer)


@mod.route('/person/<int:person_id>/event/<int:person_event_id>', methods=['GET'])
@login_required
def person_event_info(person_id, person_event_id):
    """Информация о событии привязаном к человеку"""

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    person_event = PersonEvent.query.get(person_event_id)
    if not person_event:
        abort(404)

    term_event = TermEvent.query.filter_by(
        term_id=person_event.term_id,
        event_id=person_event.event_id).first()

    return render_template(
        'term/person/event_view.html',
        person=person,
        person_event=person_event,
        person_events=PersonEvent.get_by_person_id(person.id),
        term_event=term_event,
        term_events=TermEvent().get_by_firm_id(g.firm_info['id']),
    )


@mod.route('/person/<int:person_id>/event/<int:person_event_id>', methods=['POST'])
@login_required
@json_headers
def person_event_save(person_id, person_event_id):
    """Сохраняем событие привязаное к человеку"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)

    if 'term_event_id' not in arg:
        abort(400)

    term_event_id = arg['term_event_id']

    term_event = TermEvent.query.get(term_event_id)
    if not term_event:
        abort(404)

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    if person_event_id == 0:
        person_event = PersonEvent()
    else:
        person_event = PersonEvent.query.get(person_event_id)
        if not person_event:
            abort(404)

    form = PersonEventAddForm.from_json(arg)
    if not form.validate():
        answer['message'] = u'Форма заполнена неверно, проверьте формат полей'
        return jsonify(answer)

    form.populate_obj(person_event)
    person_event.term_id = term_event.term_id
    person_event.event_id = term_event.event_id
    person_event.firm_id = g.firm_info['id']

    person_event_old = PersonEvent.query.filter_by(
        person_id=person.id,
        term_id=term_event.term_id,
        event_id=term_event.event_id).first()

    if person_event_old and (person_event.id != person_event_old.id):
        answer['message'] = u"""Такое событие уже есть,
                                удалите старое или измените тип нового"""
        return jsonify(answer)

    if person_event.save():
        answer['error'] = 'no'
        answer['message'] = u'Данные сохранены'
        return jsonify(answer)

    return jsonify(answer)


@mod.route('/person/<int:person_id>/event/<int:person_event_id>/delete', methods=['POST'])
@login_required
@json_headers
def person_event_delete(person_id, person_event_id):
    """Удаляем событие привязаное к человеку"""

    answer = dict(error='yes', message='Произошла ошибка')

    person_event = PersonEvent.query.filter_by(
        person_id=person_id, id=person_event_id).first()

    if not person_event:
        abort(404)

    person_event.delete()
    answer['error'] = 'no'
    answer['message'] = u'Событие удалено'

    return jsonify(answer)


@mod.route('/person/<int:person_id>/wallet/save', methods=['POST'])
@login_required
@json_headers
def person_save_corp_wallet(person_id):
    """Добавляем или редактируем корпоративный кошелёк"""

    answer = dict(error='yes', message=u'Произошла ошибка')
    arg = get_post_arg(request, True)

    person_limit = arg['limit'] if 'limit' in arg else False
    if not person_limit:
        abort(405)

    interval = arg[
        'interval'] if 'interval' in arg else TermCorpWallet.INTERVAL_ONCE

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    interval = int(interval)
    person_limit = int(person_limit)
    max_limit = TermCorpWallet().get_max_limit_dict()
    if person_limit > max_limit[interval]:
        answer['message'] = u'Превышен лимит'
        return jsonify(answer)

    corp_wallet = TermCorpWallet.query.filter_by(person_id=person.id).first()

    if not corp_wallet:
        corp_wallet = TermCorpWallet()
        corp_wallet.person_id = person.id

    corp_wallet.balance = int(person_limit) * 100
    corp_wallet.interval = interval
    corp_wallet.limit = corp_wallet.balance
    corp_wallet.status = TermCorpWallet.STATUS_ACTIVE

    person.wallet_status = Person.STATUS_VALID
    person.type = Person.TYPE_WALLET

    person_events = PersonEvent.get_by_person_id(person.id)
    for person_event in person_events:
        person_event.timeout = 0
        person_event.save()

    if person.save() and corp_wallet.save():
        answer['error'] = 'no'
        answer['message'] = u'Операция выполнена'
        answer['corp_wallet'] = corp_wallet.to_json()
        answer['content'] = render_template(
            'term/person/wallet/_view.html',
            corp_wallet=corp_wallet,
            corp_wallet_interval=TermCorpWallet().get_interval_list())

    return jsonify(answer)


@mod.route('/person/<int:person_id>/wallet/remove', methods=['POST'])
@login_required
@json_headers
def person_remove_corp_wallet(person_id):
    """Удаляем корпоративный кошелёк"""

    answer = dict(error='yes', message='Произошла ошибка')
    arg = get_post_arg(request, True)

    wallet_id = arg['id'] if 'id' in arg else False

    if not wallet_id:
        abort(405)

    person = Person.query.get(person_id)
    if not person:
        abort(404)

    if person.type == Person.TYPE_WALLET:
        person.type = Person.TYPE_TIMEOUT
        person.wallet_status = Person.STATUS_VALID

    corp_wallet = TermCorpWallet.query.get(wallet_id)
    if corp_wallet:
        corp_wallet.delete()
        if person.save():
            answer['error'] = 'no'
            answer['message'] = u'Корпоративный кошелек удален'

    return jsonify(answer)


@mod.route('/person/<int:person_id>/report/', methods=['POST'])
@login_required
@json_headers
def person_report(person_id):
    """Отчет по операциям человека"""

    arg = get_post_arg(request, True)

    arg['type'] = 'person'
    arg['id'] = person_id
    answer = Report().get_person_report(**arg)

    return jsonify(answer)


@mod.route('/person/search/', methods=['POST'])
@login_required
@json_headers
def person_search():
    """Поиск человека"""

    arg = get_post_arg(request, True)
    answer = dict(error='yes', content='')
    if 'person_name' not in arg:
        abort(400)

    answer['content'] = 'no'
    answer['content'] = Person.get_by_firm_id_search(g.firm_info['id'], arg['person_name'])
    return jsonify(answer)
