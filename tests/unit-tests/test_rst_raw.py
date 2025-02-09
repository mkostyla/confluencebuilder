# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceRstRaw(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceRstRaw, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')

    @setup_builder('confluence')
    def test_storage_rst_raw_default(self):
        out_dir = self.build(self.dataset, filenames=['raw-storage'])

        with parse('raw-storage', out_dir) as data:
            strong = data.find('strong')
            self.assertIsNotNone(strong)
            self.assertEqual(strong.text, 'raw content')
