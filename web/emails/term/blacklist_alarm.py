# -*- coding: utf-8 -*-
"""
    Класс сообщения для оповещения о блокировке кошелька

    :copyright: (c) 2015 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""

from flask import render_template
from flask.ext.mail import Message


class BlacklistAlarmMessage(Message):

    @classmethod
    def desc(cls):
        return 'blacklist alarm'

    def __init__(self, **kwargs):
        required = ['to', 'lang', 'spotname', 'username', 'amount', 'card_pan']
        for k in required:
            if not k in kwargs:
                msg = "These values must be provided: %s" % ",".join(required)
                raise KeyError(msg)

        lang = kwargs['lang']
        if lang == 'ru':
            title = u'Спот заблокирован'
            template = 'term/emails/blacklist/ru_blacklist_alarm.html'
        else:
            title = u'Spot blocked'
            template = 'term/emails/blacklist/en_blacklist_alarm.html'
        Message.__init__(self, title)

        self.add_recipient(kwargs['to'])

        self.html = render_template(template, **kwargs)
