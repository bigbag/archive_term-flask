# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, терминалы фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *
from models.term import Term


@mod.route('/terminal', methods=['GET'])
@login_required
def terminal_view():
    """таблица имеющихся у фирмы терминалов"""
    firm_info = g.firm_info

    return render_template(
        'term/terminal/view.html',
        firm_name=firm_info['name'],
        user_email=g.user.email)


@mod.route('/terminal', methods=['POST'])
@login_required
@json_headers
def get_term_list():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    answer = Term().select_term_list(
        firm_info['id'], **arg)

    return jsonify(answer)
