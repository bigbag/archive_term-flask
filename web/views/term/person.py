# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, люди фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *

from models.person import Person


@mod.route('/person/<path:action>', methods=['GET'])
@mod.route('/person', methods=['GET'])
@login_required
def person_view(action=None):
    """Отображаем страницу со списком сотрудников, сам список получаем отдельным запросом"""

    return render_template(
        'term/person/index.html'
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
