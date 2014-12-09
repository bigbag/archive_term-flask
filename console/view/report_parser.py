# -*- coding: utf-8 -*-
"""
    Консольное приложение для генерации отчетов

    :copyright: (c) 2014 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
from flask.ext.script import Command

from console import app

from web.tasks.report_parser import ReportParserTask


class ReportParser(Command):

    "Report parser"

    def run(self):
        report_path = app.config['REPORT_TMP_PACH']
        files_all = os.listdir(report_path)
        for file_name in files_all:
            file_name = "%s/%s" % (report_path, file_name)
            ReportParserTask.report_manager.delay(file_name)
