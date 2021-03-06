# -*- coding: utf-8 -*-
"""
    Хелпер для работы с url и запросами к внешним ресурсам

    :copyright: (c) 2014 by Denis Amelin,  Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from grab import Grab
import json


def clear_get_params(answer):
    keys = ("/", "?", "&")
    for key in keys:
        if key in answer:
            answer = answer[0:answer.find(key)]
            break

    return answer


def parse_get_param(value, param):
    if param in value:
        value = value[value.find(param) + len(param):]

    value = clear_get_params(value)

    return value


def make_request(url, parse_json):
    g = Grab()
    g.go(url)
    answer = g.response.body
    if parse_json:
        answer = json.loads(answer)

    return answer


def name_together(person):
    new_person = person.copy()
    if 'name' in new_person and 'second_name' in new_person and 'patronymic' in new_person:
        fullName = new_person['second_name'] if len(
            new_person['second_name']) else u''

        if len(fullName):
            fullName = fullName + u' ' + \
                new_person['name'] if len(new_person['name']) else fullName
        elif len(new_person['name']):
            fullName = new_person['name']

        if len(fullName):
            fullName = fullName + u' ' + \
                new_person['patronymic'] if len(
                    new_person['patronymic']) else fullName
        elif len(new_person['patronymic']):
            fullName = new_person['patronymic']

        new_person['name'] = fullName
        del new_person['second_name']
        del new_person['patronymic']

    return new_person
