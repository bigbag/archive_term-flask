# -*- coding: utf-8 -*-
"""
    Хелпер для работы с сигнатурами

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import hashlib
import base64


def get_content_md5(data):
    m = hashlib.md5()
    m.update(data)
    signature = base64.b64encode(m.digest())
    return signature
