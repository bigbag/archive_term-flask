# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, терминалы фасад

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *
from models.term import Term
from models.firm_term import FirmTerm


@mod.route('/terminal', methods=['GET'])
@login_required
def terminal_view():
    """Таблица имеющихся у фирмы терминалов"""

    return render_template('term/terminal/view.html')


@mod.route('/terminal/<int:term_id>', methods=['GET'])
@login_required
def terminal_info(term_id):
    """Информация о терминале"""
    firm_info = g.firm_info

    if not term_id in FirmTerm().get_list_by_firm_id(firm_info['id']):
        abort(403)

    return render_template('term/terminal/info.html')


@mod.route('/terminal', methods=['POST'])
@login_required
@json_headers
def get_term_list():
    firm_info = g.firm_info
    arg = json.loads(request.stream.read())
    answer = Term().select_term_list(
        firm_info['id'], **arg)

    return jsonify(answer)
