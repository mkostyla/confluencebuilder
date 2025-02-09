# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2018-2021 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from pkg_resources import parse_version
from sphinx.__init__ import __version__ as sphinx_version
from tests.lib import build_sphinx
from tests.lib import enable_sphinx_info
from tests.lib import prepare_conf
from tests.lib import prepare_dirs
import os
import sys
import unittest

DEFAULT_TEST_DESC = 'test state'
DEFAULT_TEST_KEY = 'test-holder'
DEFAULT_TEST_SPACE = 'DEVELOP'
DEFAULT_TEST_URL = 'https://sphinxcontrib-confluencebuilder.atlassian.net/wiki/'
DEFAULT_TEST_USER = 'sphinxcontrib-confluencebuilder@jdknight.me'
DEFAULT_TEST_VERSION = 'master'
AUTH_ENV_KEY = 'CONFLUENCE_AUTH'
SPACE_ENV_KEY = 'CONFLUENCE_SPACE'
TESTDESC_ENV_KEY = 'CONFLUENCE_TEST_DESC'
TESTKEY_ENV_KEY = 'CONFLUENCE_TEST_KEY'
TESTKEY_ENV_VERSION = 'CONFLUENCE_TEST_VERSION'


class TestConfluenceValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        enable_sphinx_info()

        # build configuration
        space_key = os.getenv(SPACE_ENV_KEY, DEFAULT_TEST_SPACE)
        cls.config = prepare_conf()
        cls.config['confluence_disable_notifications'] = True
        cls.config['confluence_page_hierarchy'] = True
        cls.config['confluence_page_generation_notice'] = True
        cls.config['confluence_parent_page'] = None
        cls.config['confluence_prev_next_buttons_location'] = 'both'
        cls.config['confluence_publish'] = True
        cls.config['confluence_server_pass'] = os.getenv(AUTH_ENV_KEY)
        cls.config['confluence_server_url'] = DEFAULT_TEST_URL
        cls.config['confluence_server_user'] = DEFAULT_TEST_USER
        cls.config['confluence_sourcelink'] = {
            'type': 'github',
            'owner': 'sphinx-contrib',
            'repo': 'confluencebuilder',
            'container': 'tests/validation-sets/',
        }
        cls.config['confluence_space_key'] = space_key
        cls.config['confluence_timeout'] = 10
        cls.config['imgmath_font_size'] = 14
        cls.config['imgmath_image_format'] = 'svg'
        cls.config['imgmath_use_preview'] = True
        cls.config['manpages_url'] = 'https://example.org/{path}'
        cls.test_desc = os.getenv(TESTDESC_ENV_KEY, DEFAULT_TEST_DESC)
        cls.test_key = os.getenv(TESTKEY_ENV_KEY, DEFAULT_TEST_KEY)
        cls.test_version = os.getenv(TESTKEY_ENV_KEY, DEFAULT_TEST_VERSION)

        # overrides from user
        try:
            from validation_test_overrides import config_overrides
            cls.config.update(config_overrides)
        except ImportError:
            pass
        try:
            from validation_test_overrides import config_test_desc
            cls.test_desc = config_test_desc
        except ImportError:
            pass
        try:
            from validation_test_overrides import config_test_key
            cls.test_key = config_test_key
        except ImportError:
            pass
        try:
            from validation_test_overrides import config_test_version
            cls.test_version = config_test_version
        except ImportError:
            pass

        # finalize
        if cls.config['confluence_space_key'].startswith('~'):
            cls.config['confluence_root_homepage'] = False
        cls.config['confluence_publish_prefix'] = ''
        cls.config['confluence_publish_postfix'] = ''
        cls.config['confluence_purge'] = False
        cls.config['confluence_sourcelink']['version'] = cls.test_version
        cls.config['rst_epilog'] = """
.. |test_key| replace:: {}
.. |test_desc| replace:: {}
""".format(cls.test_key, cls.test_desc)

        # find validate-sets base folder
        test_dir = os.path.dirname(os.path.realpath(__file__))
        cls.datasets = os.path.join(test_dir, 'validation-sets')

        # setup base structure
        dataset = os.path.join(cls.datasets, 'base')
        doc_dir = prepare_dirs('validation-set-base')

        config = cls.config.clone()
        config['confluence_sourcelink']['container'] += 'base/'

        # inject a navdoc from the "standard" start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_next', 'Standard', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        # build/publish test base page
        build_sphinx(dataset, config=config, out_dir=doc_dir)

        # finalize configuration for tests
        cls.config['confluence_parent_page'] = cls.test_key
        cls.config['confluence_purge'] = True
        cls.config['confluence_purge_from_root'] = True
        cls.config['confluence_root_homepage'] = False

    def test_extended_autodocs(self):
        if parse_version(sphinx_version) < parse_version('2.3.1'):
            raise unittest.SkipTest('breathe requires sphinx>=2.3.1')

        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'extended-autodocs/'
        config['extensions'].append('breathe')
        config['extensions'].append('sphinx.ext.autodoc')

        # inject a navdoc from the last header/footer page, to the
        # extended autodocs start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'sphinx.ext.todo', None)
            docnames.insert(0, '_validation_prev')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        dataset = os.path.join(self.datasets, 'extended-autodocs')
        doc_dir = prepare_dirs('validation-set-extended-autodocs')
        xml_dir = os.path.join(dataset, 'xml')

        config['breathe_projects'] = {}
        for name in os.listdir(xml_dir):
            sample_dir = os.path.join(xml_dir, name)
            if os.path.isdir(sample_dir):
                config['breathe_projects'][name] = sample_dir

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def test_extensions(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'extensions/'
        config['extensions'].append('sphinx.ext.autodoc')
        config['extensions'].append('sphinx.ext.autosummary')
        config['extensions'].append('sphinx.ext.graphviz')
        config['extensions'].append('sphinx.ext.ifconfig')
        config['extensions'].append('sphinx.ext.inheritance_diagram')
        config['extensions'].append('sphinx.ext.todo')
        config['graphviz_output_format'] = 'svg'
        config['todo_include_todos'] = True
        config['todo_link_only'] = True

        # inject a navdoc from the last header/footer page, to the
        # extended autodocs start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Markdown Table', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Extended - autodocs', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        dataset = os.path.join(self.datasets, 'extensions')
        doc_dir = prepare_dirs('validation-set-extensions')
        sys.path.insert(0, os.path.join(dataset, 'src'))

        build_sphinx(dataset, config=config, out_dir=doc_dir)

        sys.path.pop(0)

    def test_header_footer(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'header-footer/'

        dataset = os.path.join(self.datasets, 'header-footer')
        doc_dir = prepare_dirs('validation-set-hf')

        config['confluence_header_file'] = os.path.join(dataset, 'header.tpl')
        config['confluence_footer_file'] = os.path.join(dataset, 'footer.tpl')

        # inject a navdoc from the last "standard (no macro)" page, to the
        # hierarchy example start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Verification of content (nomacro)', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Hierarchy example', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def test_hierarchy(self):
        config = self.config.clone()
        config['confluence_max_doc_depth'] = 2
        config['confluence_page_hierarchy'] = True
        config['confluence_sourcelink']['container'] += 'hierarchy/'

        # inject a navdoc from the last "standard (no macro)" page, to the
        # hierarchy example start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Header/footer example (page c)', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Markdown', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        dataset = os.path.join(self.datasets, 'hierarchy')
        doc_dir = prepare_dirs('validation-set-hierarchy')

        build_sphinx(dataset, config=config, out_dir=doc_dir, relax=True)

    def test_markdown(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'markdown/'
        config['extensions'].append('myst_parser')

        dataset = os.path.join(self.datasets, 'markdown')
        doc_dir = prepare_dirs('validation-set-markdown')

        # inject a navdoc from the last "standard (no macro)" page, to the
        # hierarchy example start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Hierarchy example (d)', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Extensions', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def test_standard_default(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'standard/'

        dataset = os.path.join(self.datasets, 'standard')
        doc_dir = prepare_dirs('validation-set-standard')

        # inject a navdoc to the "standard (no macro)" page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', self.test_key, None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Standard (nomacro)', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)

    def test_standard_macro_restricted(self):
        config = self.config.clone()
        config['confluence_sourcelink']['container'] += 'standard/'

        dataset = os.path.join(self.datasets, 'standard')
        doc_dir = prepare_dirs('validation-set-standard-nm')

        config['confluence_adv_restricted'] = [
            'anchor',
            'children',
            'code',
            'info',
            'viewfile',
            'jira'
        ]
        config['confluence_header_file'] = os.path.join(dataset, 'no-macro.tpl')
        config['confluence_publish_postfix'] = ' (nomacro)'

        # inject a navdoc from the last "standard" page, to the header/footer
        # start page
        def navdocs_transform(builder, docnames):
            builder.state.register_title(
                '_validation_prev', 'Verification of content', None)
            docnames.insert(0, '_validation_prev')
            builder.state.register_title(
                '_validation_next', 'Header/footer example', None)
            docnames.append('_validation_next')
            return docnames
        config['confluence_navdocs_transform'] = navdocs_transform

        build_sphinx(dataset, config=config, out_dir=doc_dir)


if __name__ == '__main__':
    sys.exit(unittest.main(failfast=True, verbosity=0))
