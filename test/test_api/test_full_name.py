"""
Tests for :attr:`.BaseDefinition.full_name`.

There are three kinds of test:

#. Test classes derived from :class:`MixinTestFullName`.
   Child class defines :attr:`.operation` to alter how
   the api definition instance is created.

#. :class:`TestFullDefinedName` is to test combination of
   ``obj.full_name`` and ``jedi.defined_names``.

#. Misc single-function tests.
"""

import textwrap

import pytest

import jedi
from ..helpers import TestCase


class MixinTestFullName(object):
    operation = None

    def check(self, source, desired):
        script = jedi.Script(textwrap.dedent(source))
        definitions = getattr(script, type(self).operation)()
        self.assertEqual(definitions[0].full_name, desired)

    def test_os_path_join(self):
        self.check('import os; os.path.join', 'os.path.join')

    def test_builtin(self):
        self.check('type', 'type')

    def test_from_import(self):
        self.check('from os import path', 'os.path')


class TestFullNameWithGotoDefinitions(MixinTestFullName, TestCase):
    operation = 'goto_definitions'

    @pytest.mark.skipif('sys.version_info[0] < 3', reason='Python 2 also yields None.')
    def test_tuple_mapping(self):
        self.check("""
        import re
        any_re = re.compile('.*')
        any_re""", 're.RegexObject')


class TestFullNameWithCompletions(MixinTestFullName, TestCase):
    operation = 'completions'


class TestFullDefinedName(TestCase):
    """
    Test combination of ``obj.full_name`` and ``jedi.defined_names``.
    """

    def check(self, source, desired):
        definitions = jedi.defined_names(textwrap.dedent(source))
        full_names = [d.full_name for d in definitions]
        self.assertEqual(full_names, desired)

    def test_local_names(self):
        self.check("""
        def f(): pass
        class C: pass
        """, ['f', 'C'])

    def test_imports(self):
        self.check("""
        import os
        from os import path
        from os.path import join
        from os import path as opath
        """, ['os', 'os.path', 'os.path.join', 'os.path'])
