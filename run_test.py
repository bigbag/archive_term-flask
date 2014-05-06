# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска теста

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import unittest
from test import *

loader = unittest.TestLoader()

models_general_test = loader.loadTestsFromModule(models_general_test)
models_term_test = loader.loadTestsFromModule(models_term_test)
models_payment_test = loader.loadTestsFromModule(models_payment_test)

api_term_test = loader.loadTestsFromModule(api_term_test)
api_admin_test = loader.loadTestsFromModule(api_admin_test)

web_term_test = loader.loadTestsFromModule(web_term_test)

tests = [
    models_general_test,
    models_payment_test,
    models_term_test,
    api_admin_test,
    api_term_test,
    web_term_test]

# tests = [web_yandex_test]

alltests = unittest.TestSuite(tests)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(alltests)
