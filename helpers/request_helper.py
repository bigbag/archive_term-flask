# -*- coding: utf-8 -*-
"""
    Хелпер для работы с url и запросами к внешним ресурсам

    :copyright: (c) 2014 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from grab import Grab
import json


def clear_get_params(str):

    answer = str
    if "/" in answer:
        answer = answer[0:answer.find("/")]
    if "?" in answer:
        answer = answer[0:answer.find("?")]
    if "&" in answer:
        answer = answer[0:answer.find("&")]

    return answer


def parse_get_param(url, param):
    value = url
    if param in value:
        value = value[value.find(param) + len(param):]

    if "/" in value:
        value = value[0:value.find("/")]
    if "?" in value:
        value = value[0:value.find("?")]
    if "&" in value:
        value = value[0:value.find("&")]

    return value


def make_request(url, parse_json):
    g = Grab()
    g.go(url)
    answer = g.response.body
    if parse_json:
        answer = json.loads(answer)

    return answer
