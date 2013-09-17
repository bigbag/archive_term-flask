# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, сотрудники

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *


@login_required
def get_index():
    """Главная страница"""
    firm_info = session['firm_info']
    return render_template(
        'term/person/list.html',
        firm_name=firm_info['name'],
        user_email=g.user.email)
