# -*- coding: utf-8 -*-
"""
    Входной скрипт для запуска теста

    :copyright: (c) 2013 by Pavel Lyashkov.
    :license: BSD, see LICENSE for more details.
"""

import unittest
from test import *

loader = unittest.TestLoader()

web_test = loader.loadTestsFromModule(web_test)
models_test = loader.loadTestsFromModule(models_test)
models_term_test = loader.loadTestsFromModule(models_term_test)
models_payment_test = loader.loadTestsFromModule(models_payment_test)
tests = [web_test, models_test, models_payment_test, models_term_test]

alltests = unittest.TestSuite(tests)

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(alltests)