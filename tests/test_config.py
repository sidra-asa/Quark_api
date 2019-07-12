#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import unittest
from utils.config import Config


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.c = Config()

    def test_get_option_exist(self):
        """Fetch an option of each type from default config file."""
        self.assertEqual(self.c.get('db').get('db'), "Quark")
