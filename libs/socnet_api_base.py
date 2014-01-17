# -*- coding: utf-8 -*-
"""
    Базовый класс для библиотек работы с соцсетями

    :copyright: (c) 2013 by Denis Amelin.
    :license: BSD, see LICENSE for more details.
"""
from grab import Grab
import json


class SocnetApiBase():

    @staticmethod
    def rmGetParams(str):
        answer = str
        if "/" in answer:
            answer = answer[0:answer.find("/")]
        if "?" in answer:
            answer = answer[0:answer.find("?")]
        if "&" in answer:
            answer = answer[0:answer.find("&")]

        return answer

    @staticmethod
    def parse_get_param(url, param):
        value = url
        if param in value:
            value = value[value.find(param) + len(param):]

        value = SocnetApiBase.rmGetParams(value)

        return value
