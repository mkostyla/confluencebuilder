# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2020-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from tests.lib.testcase import ConfluenceTestCase
from tests.lib.testcase import setup_builder
from tests.lib import parse
import os


class TestConfluenceSphinxVersionAdded(ConfluenceTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestConfluenceSphinxVersionAdded, cls).setUpClass()

        cls.dataset = os.path.join(cls.datasets, 'common')
        cls.filenames = [
            'versionadded',
        ]

    @setup_builder('confluence')
    def test_storage_sphinx_versionadded_defaults(self):
        out_dir = self.build(self.dataset, filenames=self.filenames)

        with parse('versionadded', out_dir) as data:
            note_macro = data.find('ac:structured-macro', {'ac:name': 'info'})
            self.assertIsNotNone(note_macro)

            rich_body = note_macro.find('ac:rich-text-body')
            self.assertIsNotNone(rich_body)

            text_contents = rich_body.text.strip()
            self.assertIsNotNone(text_contents)
            self.assertTrue('2.4' in text_contents)
            self.assertTrue('versionadded message' in text_contents)
