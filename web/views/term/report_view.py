# -*- coding: utf-8 -*-
"""
    Веб интерфейс терминального проекта, отчеты

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

from web.views.term.general import *


@login_required
def report_person():
    """Отчеты по сотрудникам"""
    firm_info = session['firm_info']

    return render_template(
        'term/report/person.html',
        firm_name=firm_info['name'],
        user_email=g.user.email)
