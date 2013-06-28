# -*- coding: utf-8 -*-
"""
    Консольное приложение для генерации отчетов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
from flask import Flask, render_template
from flask.ext.script import Command
from api.models.term import Term


class Report(Command):

    "Report Generation"

    def run(self):
        term = Term(21).get_term()
        return term.id
