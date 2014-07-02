# -*- coding: utf-8 -*-
"""
    Консольное приложение для генерации отчетов

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""
import os
import time
from multiprocessing.dummy import Pool as ThreadPool
from lxml import etree
from flask import Flask, render_template
from flask.ext.script import Command

from console import app

from web.tasks.report_parser import ReportParserTask

from helpers import date_helper


class ReportParser(Command):

    "Report parser"

    def run(self):
        report_path = "%s/report/" % app.config['TMP_PACH']
        files_all = os.listdir(report_path)
        for file_name in files_all:
            file_name = "%s/%s" % (report_path, file_name)
            ReportParserTask.report_manager(file_name)
